"""This module takes in the csv of team member information and creates objects 
for each person to use for other functions
"""

import pandas as pd


class Person:
    """Creates the person object with the attributes needed"""

    def __init__(self, name, role) -> None:
        self.name = name
        self.role = role

    def __repr__(self) -> str:
        """Gives a summary of the attributes of the Person object

        Returns:
            str: Returns attributes of the person object
        """
        return f"Person (Name: {self.name} - Role: {self.role})"

    def __hash__(self):
        """This allows multiple classes to be added to the set all_team in a
        future function call

        Returns:
            hash: Hash of name and role of this instance
        """
        return hash((self.name, self.role))

    def __eq__(self, other):
        """Not fully sure why this works, but I will figure it out"""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.name == other.name and self.role == other.role


class Roles:
    """Registers and assigns Person object based on their role to the correct
    ist in role_dictionary"""

    all_roles = {  # Uses a set to avoid duplicates if registering members
        # with multiple calls
        "Pod Leads": set(),
        "Snr Specialists": set(),
        "Jnr Specialists": set(),
        "Setters": set(),
    }
    all_team = set()

    def __init__(self) -> None:
        pass

    def get_setters(self):
        """Shows the name of those team members in the setter role

        Returns:
            list: Returns list of names of those in setter role
        """
        return self.all_roles["Setters"]

    def get_jnr_specialists(self):
        """Shows the name of those team members in the jnr specialist role

        Returns:
            list: Returns list of names of those in jnr specialist role
        """
        return self.all_roles["Jnr Specialists"]

    def get_snr_specialists(self):
        """Shows the name of those team members in the snr specialist role

        Returns:
            list: Returns list of names of those in snr specialist role
        """
        return self.all_roles["Snr Specialists"]

    def get_pod_leads(self):
        """Shows the name of those team members in the Pod Lead role

        Returns:
            list: Returns list of names of those in Pod Lead role
        """
        return self.all_roles["Pod Leads"]

    def parse_csv_of_roles(self):
        """Uses csv as a database to pull through data for each team member

        Returns:
            dataframe: Returns two columns, name and role
        """
        df = pd.read_csv(
            "/Users/louisrae/Documents/team_scripts/dfysetters/db_people.csv"
        )
        return df

    def register_member(self, team_member: Person):
        """Takes the Person object and assigns the attributes to the
        role dictionary and object to a list of all team_members

        Args:
            team_member (Person): Takes in Person object, defined above
        """
        self.all_roles[team_member.role].add(team_member.name)
        self.all_team.add(team_member)

    def register_all_members(self):
        """Registers every member into dictionary and full list who
        is in database
        """
        for name, role in self.parse_csv_of_roles().values:
            person = Person(name, role)
            self.register_member(person)
