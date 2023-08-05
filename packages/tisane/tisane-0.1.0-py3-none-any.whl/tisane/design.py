from pandas.core.frame import DataFrame
from tisane.variable import (
    AbstractVariable,
    SetUp,
    Unit,
    Nominal,
    Ordinal,
    Has,
    Nests,
    Repeats,
)
from tisane.graph import Graph
from tisane.data import Dataset

import os
from typing import List
import typing  # to use typing.Union; Union is overloaded in z3
import pandas as pd
import pydot

"""
Class for expressing (i) data collection structure, (ii) that there is a manipulation and (iii) how there is a manipulation (e.g., between-subjects, within-subjects)
Relies on Class Treatment, Nests, Repeats
"""

interaction_effects = list()


class Design(object):
    """Represents your study design

    Parameters
    ----------
    dv : AbstractVariable
        The **d**\ ependent **v**\ ariable.
    ivs : List[AbstractVariable]
        A list of the **i**\ ndependent **v**\ ariable(s).
    source : os.PathLike or pd.DataFrame, optional
        For internal use only.

    Attributes
    ----------
    graph : Graph
        The underlying graph representation of the variables in the design.
    dataset : Dataset
        The data for your study, if you have any.
    dv : AbstractVariable
        The dependent variable in the study design
    ivs : List[AbstractVariable]
        The independent variable(s), if any, in your study design

    """

    dv: AbstractVariable
    ivs: List[AbstractVariable]
    graph: Graph  # IR
    dataset: Dataset

    def __init__(
        self,
        dv: AbstractVariable,
        ivs: List[AbstractVariable],
        source: typing.Union[os.PathLike, pd.DataFrame] = None,
    ):
        self.dv = dv

        self.ivs = ivs  # TODO: May want to replace this if move away from Design as Query object

        self.graph = Graph()  # empty graph

        # Add all variables to the graph
        # Add dv
        self._add_variable_to_graph(self.dv)
        # Add all ivs
        for v in ivs:
            self._add_variable_to_graph(v)

        # Add any nesting relationships involving IVs that may be implicit
        self._add_nesting_relationships_to_graph()

        # Add variables that the identifiers have
        self._add_identifiers_has_relationships_to_graph()

        if source is not None:
            self.dataset = Dataset(source)
            # Check and update cardinality for variables in this design
            self.check_variable_cardinality()
        else:
            self.dataset = None

    def __str__(self):
        ivs_descriptions = list()
        for v in self.ivs:
            ivs_descriptions.append(str(v))
        ivs_descriptions_str = "\n".join(ivs_descriptions)

        dv_description = str(self.dv)
        description = (
            f"dependent variable: {dv_description}"
            + "\n"
            + f"independent variables: {ivs_descriptions_str}"
            + "\n"
            + f"data: {self.data}"
        )

        return description

    # Calculates and assigns cardinality to variables if cardinality is not already specified
    # If calculated cardinality differs from cardinality estimated from the data, raises a ValueError
    def check_variable_cardinality(self):
        assert self.dataset is not None
        assert isinstance(self.dataset, Dataset)

        variables = self.graph.get_variables()

        for v in variables:
            if isinstance(v, Nominal):
                # If cardinality was not specified previously, calculate it
                if v.cardinality is None:
                    v.assign_cardinality_from_data(self.dataset)

                # If categories were not specified previously, calculate it
                if v.categories is None:
                    v.assign_categories_from_data(self.dataset)

                # Check now
                calculated_cardinality = v.calculate_cardinality_from_data(
                    data=self.dataset
                )
                calculated_categories = v.calculate_categories_from_data(
                    data=self.dataset
                )
                assert calculated_cardinality == len(calculated_categories)

                if calculated_cardinality > v.cardinality:
                    diff = calculated_cardinality - v.cardinality
                    raise ValueError(
                        f"Variable {v.name} is specified to have cardinality = {v.cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} more categories in the data than you expect."
                    )
                # It is ok for there to be fewer categories (not all categories may be represented in the data) than the user expected

                # Are there more categories than the user specified?
                if not v.isInteraction:
                    diff = set(calculated_categories) - set(v.categories)
                    if len(diff) > 0:

                        raise ValueError(
                            f"Variable {v.name} is specified to have the following categories: {v.categories}. However, in the data provided, {v.name} has {calculated_categories} unique values. These are the categories that exist in the data but you may not have expected: {diff}"
                        )
                # It is ok for there to be fewer categories (not all categories may be represented in the data) than the user expected

            elif isinstance(v, Ordinal):
                calculated_cardinality = v.calculate_cardinality_from_data(
                    data=self.dataset
                )

                if calculated_cardinality > v.cardinality:
                    diff = calculated_cardinality - v.cardinality
                    raise ValueError(
                        f"Variable {v.name} is specified to have cardinality = {v.cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} more categories in the data than you expect."
                    )
                # It is ok for there to be fewer categories (not all categories may be represented in the data) than the user expected

            elif isinstance(v, Unit):
                # If cardinality was not specified previously, calculate it
                if v.cardinality is None:
                    v.assign_cardinality_from_data(self.dataset)

                calculated_cardinality = v.calculate_cardinality_from_data(
                    data=self.dataset
                )

                if calculated_cardinality != v.cardinality:
                    diff = calculated_cardinality - v.cardinality
                    raise ValueError(
                        f"Unit {v.name} is specified to have cardinality = {v.cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} more instances of the unit in the data than you expect."
                    )
            elif isinstance(v, SetUp):
                v_cardinality = v.get_cardinality()
                # If cardinality was not specified previously, calculate it
                if v_cardinality is None:
                    v.assign_cardinality_from_data(self.dataset)

                calculated_cardinality = v.calculate_cardinality_from_data(
                    data=self.dataset
                )

                if calculated_cardinality != v_cardinality:
                    diff = calculated_cardinality - v_cardinality
                    if diff > 0:
                        raise ValueError(
                            f"SetUp {v.name} is specified to have cardinality = {v_cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} more instances of the setting in the data than you expect."
                        )
                    else:
                        assert diff < 0
                        raise ValueError(
                            f"SetUp {v.name} is specified to have cardinality = {v_cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} fewer instances of the setting in the data than you expect."
                        )
            # else:
            # import pdb; pdb.set_trace()

    # Associate this Study Design with a Dataset
    def assign_data(self, source: typing.Union[os.PathLike, pd.DataFrame]):
        """Associate this study design with a dataset

        Assigning data to the study design allows Tisane to perform
        some additional checks on your study design and variables,
        and ensures that everything makes sense.

        It is optional to specify cardinality for variables, and
        the `Design` will automatically calculate the cardinality
        using the data.

        When cardinality is specified, the `Design` will check
        to make sure that the cardinality of the variable and the
        cardinality in the data make sense.

        Parameters
        ----------
        source : os.PathLike or pandas.DataFrame
            How to get the data. This can be a string containing
            a path, such as "path/to/my/data.csv", or some kind of path object, or simply a `Pandas DataFrame <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_.
            If it is a path, it must be a csv file.

        Returns
        -------
        Design
            A reference to the object this was called on

        Examples
        --------

        Our data is in a csv file called "rats_data.csv".

        >>> import tisane as ts
        >>> rat = ts.Unit("rat_id")
        >>> week = ts.SetUp("week_number")
        >>> weight = rat.numeric("rat_weight", number_of_instances=week)
        >>> exercise_condition = rat.nominal("exercise_condition")
        >>> design = ts.Design(ivs=[exercise_condition], dv=weight).assign_data("rats_data.csv")

        Suppose instead we have a pandas `DataFrame` called `rats_df`.

        >>> design = ts.Design(ivs=[exercise_condition], dv=weight).assign_data(rats_df)

        """
        self.dataset = Dataset(source)

        self.check_variable_cardinality()

        return self

    def has_data(self) -> bool:
        return self.dataset is not None

    def get_data(self) -> pd.DataFrame:
        if self.dataset is not None:
            return self.dataset.get_data()
        # else
        return None

    def _add_variable_to_graph(self, variable: AbstractVariable):
        for r in variable.relationships:
            self.graph.add_relationship(relationship=r)

    def _add_nesting_relationships_to_graph(self):
        variables = self.graph.get_variables()

        for v in variables:
            relationships = v.relationships

            for r in relationships:
                if isinstance(r, Nests):
                    self.graph.add_relationship(relationship=r)

    def _add_identifiers_has_relationships_to_graph(self):
        identifiers = self.graph.get_identifiers()

        for unit in identifiers:
            # Does this unit have any other relationships/edges not already in the graph?
            relationships = unit.relationships

            for r in relationships:
                if isinstance(r, Has):
                    measure = r.measure
                    if not self.graph.has_edge(
                        start=unit, end=measure, edge_type="has"
                    ):
                        self.graph.add_relationship(relationship=r)

    # def _add_ivs(self, ivs: List[typing.Union[Treatment, AbstractVariable]]):

    #     for i in ivs:
    #         if isinstance(i, AbstractVariable):
    #             # TODO: Should the default be 'associate' instead of 'contribute'??
    #             self.graph.contribute(lhs=i, rhs=self.dv)

    #         elif isinstance(i, Treatment):
    #             unit = i.unit
    #             treatment = i.treatment

    #             self.graph.treat(unit=unit, treatment=treatment, treatment_obj=i)

    #             # Add treatment edge
    #             self.graph.contribute(lhs=treatment, rhs=self.dv)

    def _add_groupings(self, groupings: List[typing.Union[Nests, Repeats]]):
        for g in groupings:

            if isinstance(g, Nests):
                unit = g.unit
                group = g.group

                self.graph.nests(unit=unit, group=group, nest_obj=g)

            elif isinstance(g, Repeats):
                unit = g.unit
                response = g.response

                self.graph.repeat(unit=unit, response=response, repeat_obj=g)

    # TODO: Should be class method?
    # Create Design object from a @param Graph object
    # Useful for when moving between states Design - Graph - StatisticalModel
    # E.g., gr = infer_from(design, 'variable relationship graph') then infer_from (gr, 'statistical model')
    # TODO: Not sure if @param graph could be StatisticalModel as well...?
    def create_from(graph: Graph):
        raise NotImplementedError

        # Might have some logical facts "baked in" so would not have to ask for the same facts all the time...?
        # Could store some of this info in the edges? or as separate properties/piv?

        # TODO: Update rest of object in order to reflect updates to graph

    # @return IV and DV variables
    def get_variables(self):
        variables = list()
        variables = self.ivs + [self.dv]

        return variables

    def get_data_for_variable(self, variable: AbstractVariable):

        # Does design object have data?
        if self.dataset is not None:
            return self.dataset.get_column(variable.name)

        return None
        # Design object has no data, simulate data
        # return simulate_data(variable)

    # def _create_graph(self, ivs: List[AbstractVariable], dv: AbstractVariable):
    #     gr = Graph()
    #     for v in ivs:
    #         gr.contribute(v, dv)

    #     return gr

    # TODO: Any way to get rid of ivs list?
    # Add iv to self.ivs if iv is not already included
    def _add_iv(self, iv: AbstractVariable):
        if iv not in self.ivs:
            self.ivs.append(iv)
            self.graph.contribute(lhs=iv, rhs=self.dv)

    # Set self.dv to be @param dv
    # Assumes self.dv was None before
    def set_dv(self, dv: AbstractVariable):
        assert self.dv is None
        self.dv = dv
        self.graph._add_variable(dv)

    # @returns underlying graph IR
    def get_graph_ir(self):
        return self.graph

    def get_design_vis(self):
        graph = self.graph._get_graph_vis()

        edges = list(self.graph._graph.edges(data=True))  # get list of edges

        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            if edge_type == "treat":
                graph.add_edge(pydot.Edge(n0, n1, style="dotted", color="blue"))
            elif edge_type == "nests":
                graph.add_edge(pydot.Edge(n0, n1, style="dotted", color="green"))
            else:
                pass
                # raise ValueError (f"Unsupported edge type: {edge_type}")

        return graph

    def visualize_design(self):
        p_graph = self.get_design_vis()

        p_graph.write_png("design_vis.png")

    # TODO: Update if move to more atomic API
    # @returns the number of levels involved in this study design
    def get_number_of_levels(self):
        identifiers = self.graph.get_identifiers()

        return len(identifiers)
