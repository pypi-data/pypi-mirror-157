from copy import deepcopy
from typing import List
import itertools

import networkx
from metrics_layer.core.exceptions import AccessDeniedOrDoesNotExistException
from metrics_layer.core.model.base import MetricsLayerBase
from metrics_layer.core.model.definitions import Definitions
from metrics_layer.core.sql.query_errors import ParseError


class MetricsLayerDesign:
    """ """

    def __init__(self, no_group_by: bool, query_type: str, field_lookup: dict, model, project) -> None:
        self.no_group_by = no_group_by
        self.query_type = query_type
        self.field_lookup = field_lookup
        self.project = project
        self.model = model
        self.date_spine_cte_name = "date_spine"
        self.base_cte_name = "base"
        self._joins = None
        self._required_views = None

    def views(self) -> List[MetricsLayerBase]:
        return self.project.views(model=self.model)

    def joins(self) -> List[MetricsLayerBase]:
        required_views = self.required_views()

        self._join_subgraph = self.project.join_graph.subgraph(required_views)

        try:
            ordered_view_pairs = self.determine_join_order(required_views)
        except networkx.exception.NetworkXNoPath:
            raise AccessDeniedOrDoesNotExistException(
                f"There was no join path between the views: {required_views}. "
                "Check the identifiers on your views and make sure they are joinable.",
                object_name=None,
                object_type="view",
            )

        return self.project.join_graph.ordered_joins(ordered_view_pairs)

    def determine_join_order(self, required_views: list):
        if len(required_views) == 1:
            return []

        try:
            ordered_view_pairs = list(networkx.topological_sort(networkx.line_graph(self._join_subgraph)))
            ordered_view_pairs = self._clean_view_pairs(ordered_view_pairs)
            unique_joined_views = [v for p in ordered_view_pairs for v in p]

            if len(required_views) > 1 and any(v not in unique_joined_views for v in required_views):
                raise networkx.exception.NetworkXNoPath
            return ordered_view_pairs

        except networkx.exception.NetworkXUnfeasible:

            if len(required_views) == 2:
                path = self._shortest_path_between_two(required_views)
                return [(source, target) for source, target in zip(path, path[1:])]

            for view_pair in sorted(networkx.line_graph(self._join_subgraph).nodes):
                pairs = list(networkx.bfs_tree(networkx.line_graph(self._join_subgraph), view_pair))
                pairs = self._clean_view_pairs(pairs)
                unique_joined_views = [v for p in pairs for v in p]

                if all(v in unique_joined_views for v in required_views):
                    break
            return pairs

    def _shortest_path_between_two(self, required_views: list):
        valid_path_and_weights = []
        # We need to do this because we don't know a priori which is the target and which is the finish
        for start, end in itertools.permutations(required_views, 2):
            try:
                short_path = networkx.shortest_path(
                    self.project.join_graph.graph, start, end, weight="weight"
                )
                path_weight = networkx.path_weight(self.project.join_graph.graph, short_path, "weight")
                valid_path_and_weights.append((short_path, path_weight))
            except networkx.exception.NetworkXNoPath:
                pass

        if len(valid_path_and_weights) == 0:
            raise networkx.exception.NetworkXNoPath

        shortest_path = sorted(valid_path_and_weights, key=lambda x: (x[-1], "".join(x[0])))[0][0]
        return shortest_path

    def _clean_view_pairs(self, pairs: list):
        clean_pairs = []
        for i, pair in enumerate(pairs):
            included_in_query = [list(p) if j == 0 else [p[-1]] for j, p in enumerate(pairs[:i])]
            included_in_query = [v for sub_list in included_in_query for v in sub_list]
            duplicate_join = any(pair[-1] == p[-1] for p in pairs[:i])
            inverted_join = any(sorted(pair) == sorted(p) for p in pairs[:i])
            if not duplicate_join and not inverted_join and not pair[-1] in included_in_query:
                clean_pairs.append(pair)
        return clean_pairs

    def required_views(self):
        _, access_filter_fields = self.get_access_filter()
        fields_in_query = list(self.field_lookup.values()) + access_filter_fields
        return self._fields_to_unique_views(fields_in_query)

    @staticmethod
    def _fields_to_unique_views(field_list: list):
        return list(set([v for field in field_list for v in field.required_views()]))

    def deduplicate_fields(self, field_list: list):
        return self.project.deduplicate_fields(field_list)

    def functional_pk(self):
        sorted_joins = self.joins()

        if len(sorted_joins) == 0:
            return self.get_view(self.base_view_name).primary_key
        elif any(j.relationship == "many_to_many" for j in sorted_joins):
            # There is no functional primary key if there is a many_to_many join
            return Definitions.does_not_exist
        elif all(j.relationship in {"many_to_one", "one_to_one"} for j in sorted_joins):
            # The functional primary key is the key to the base join is all joins are many_to_one
            return self.get_view(self.base_view_name).primary_key
        else:
            base_view = self.get_view(self.base_view_name)
            primary_key_view_name = self._derive_primary_key_view(base_view, sorted_joins)

            if primary_key_view_name == Definitions.does_not_exist:
                return Definitions.does_not_exist
            elif primary_key_view_name != base_view.name:
                primary_key_view = self.get_view(primary_key_view_name)
                return primary_key_view.primary_key
            return base_view.primary_key

    def _derive_primary_key_view(self, base_view, sorted_joins: list):
        # if the branch is from the base and many_to_one the base is the same
        # if the branch is from a many_to_one to the base and many_to_one or one_to_one it's the same
        # if the branch is from a many_to_one to the base and one_to_many it's now many_to_many

        # if the branch is from the base and one_to_one the base is the same
        # if the branch is from a one_to_one to the base and many_to_one or one_to_one it's the same
        # if the branch is from a one_to_one to the base and one_to_many the base is the new one

        # if the branch is from the base and one_to_many the base is the new one
        # if the branch is from a one_to_many to the base and many_to_one or one_to_one it's
        #   the one referenced in the one_to_many
        # if the branch is from a one_to_many to the base and one_to_many the base is now
        #   the newest one_to_many ref

        previous_join_type = None
        base_sequence = deepcopy([base_view.name])
        for i, j in enumerate(sorted_joins):
            previous_join_type = None if i == 0 else sorted_joins[i - 1].relationship
            if j.relationship == "many_to_many":
                return Definitions.does_not_exist

            if j.relationship == "one_to_many" and previous_join_type == "many_to_one":
                return Definitions.does_not_exist
            elif j.relationship == "one_to_many":
                base_sequence.append(j.join_view_name)
        primary_key = base_sequence[-1]
        return primary_key

    def get_view(self, name: str) -> MetricsLayerBase:
        try:
            return next(t for t in self.views() if t.name == name)
        except StopIteration:
            raise ParseError(f"View {name} not found in explore {self.explore.name}")

    def get_join(self, name: str) -> MetricsLayerBase:
        return next((j for j in self.joins() if j.name == name), None)

    def get_field(self, field_name: str) -> MetricsLayerBase:
        return self.project.get_field(field_name, model=self.model)

    def get_access_filter(self):
        views_in_request = self._fields_to_unique_views(list(self.field_lookup.values()))
        conditions, fields = [], []
        for view_name in views_in_request:
            view = self.get_view(view_name)
            if view.access_filters:
                for condition_set in view.access_filters:
                    field = self.project.get_field(condition_set["field"])
                    sql = field.sql_query(self.query_type)
                    user_attribute_value = condition_set["user_attribute"]

                    if self.project._user and self.project._user.get(user_attribute_value):
                        condition = f"{sql} = '{self.project._user[user_attribute_value]}'"
                        conditions.append(condition)
                        fields.append(field)

        if conditions and fields:
            return " and ".join(conditions), fields
        return None, []

    @property
    def base_view_name(self):
        joins = self.joins()
        if len(joins) > 0:
            return joins[0].base_view_name
        return self.required_views()[0]
