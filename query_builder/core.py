import pandas
import ipywidgets as widgets
from IPython.display import display
from astroquery.cadc import Cadc
from IPython.display import Image, display, clear_output

__all__ = ['QueryBuilder']


class QueryBuilder:

    def __init__(self, table):
        print("ADQL Builder")
        self.cadc = Cadc()
        try: 
            self.table = self._is_valid_table(table)
        except TableNotExistError:
            print("catch TableNotExistError ")
            return
        self.column_type_dictionary = {}
        self.dropdown_list = self._get_columns()
        self.combobox_list = ['a','b','c']
        self.method_list = ['like', '>', '=', '<', '<=', '>=']
        self.condition_list =[]
        self.query_output = widgets.Output()
        self.out = widgets.Output(layout=widgets.Layout(flex='1 1 auto', width='auto'))
        
        self.column_name = widgets.Dropdown(
            options=self.dropdown_list,
            description='column',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
        self.method = widgets.Dropdown(
            options=self.method_list,
            description='',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
        """self.column_value = widgets.Combobox(
            value='',
            placeholder='value',
            options=self.combobox_list,
            description='',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})"""
        
        self.column_value = widgets.Text(
            value='',
            placeholder='value',
            description='',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'))
        
        self.add_button = widgets.Button(
            description="",
            icon='plus',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(width='5%'))
        self.add_button.on_click(self._button_clicked)
        
        self.delete_button = widgets.Button(
            description="Delete",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70px'))
        self.delete_button.on_click(self._button_clicked)
        
        self.query_button = widgets.Button(
            description="Query",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70PX'))
        self.query_button.on_click(self._query_clicked)
        
        self.clear_button = widgets.Button(
            description="Clear",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70px'))
        self.clear_button.on_click(self._button_clicked)
        self.clear_button.click()
        self.ui = widgets.HBox([self.column_name, self.method, self.column_value, self.add_button])
        self.buttons_ui = widgets.VBox([self.delete_button, self.clear_button, self.query_button],layout=widgets.Layout(top = '8px'))
        self.output_ui = widgets.HBox([self.out, self.buttons_ui])
            
    def adql_builder(self):
        display(self.ui, self.output_ui, self.query_output)
    
    def _button_clicked(self, b):
        with self.out: 
            clear_output()
            if b.description == "Clear":
                self.condition_list= []

            elif b.description == "Delete":
                if len(self.condition_list) > 0:
                    self.condition_list.remove(self.conditions.value)
            else:
                self.condition_list.append(f"{self.column_name.value} {self.method.value} {self.column_value.value}")
                
            self.conditions = widgets.Select(
                    options=self.condition_list,
                    layout=widgets.Layout(flex='1 1 auto', width='auto'),
                    description='')    
            ui_condition = widgets.HBox([self.conditions])    
            display(ui_condition)
    
    def _is_valid_table(self, table_name):
        output_q = self.cadc.exec_sync(f"SELECT * From tap_schema.tables WHERE table_name='{table_name}'")
        if len(output_q) == 0:
            raise TableNotExistError
        else:
            return table_name
    
    def _query_clicked(self, b):
        with self.query_output:
            clear_output()
            Query = self.get_query()
            output = self.cadc.exec_sync(Query)
            display(output)
            #print(self.condition_list)
            #output = self.cadc.exec_sync(f"SELECT * FROM {self.table} WHERE { }"
    
        
    def get_query(self):
        Query = f"SELECT * FROM {self.table}"
        if len(self.condition_list) > 0:
            Query += " WHERE ("
        for item in self.condition_list:
            item = item.split(" ")
            if item[1] == 'like' and self.column_type_dictionary[item[0]] == 'char':
                Query += f" AND {item[0]} " + f"{item[1]} " + f"'%{str(item[2])}%'"
            elif item[1] == '=' and self.column_type_dictionary[item[0]] == 'char':
                Query += f" AND {item[0]}" + f"{item[1]}" + f"'{str(item[2])}'"
            elif self.column_type_dictionary[item[0]] == 'int':
                if item[1] == '=' or item[1] == '>' or item[1] == '<' or item[1] == '<=' or item[1] == '>=':
                    Query += f" AND {item[0]}" + f"{item[1]}" + f"{int(item[2])}"                
            elif self.column_type_dictionary[item[0]] == 'double':
                if item[1] == '=' or item[1] == '>' or item[1] == '<' or item[1] == '<=' or item[1] == '>=':
                    Query += f" AND {item[0]}" + f"{item[1]}" + f"{float(item[2])}"
        Query += ")"
        Query = Query.replace("WHERE ( AND", "WHERE (")
        print(f"Query: {Query}")
        return Query

    def _get_columns(self):
        output = self.cadc.exec_sync(f"SELECT column_name, datatype from tap_schema.columns WHERE table_name = '{self.table}' ")
        column_lst = list(output['column_name'])
        type_lst = list(output['datatype'])
        for i in range(0, len(column_lst)):
            self.column_type_dictionary[column_lst[i]] = type_lst[i]
        return column_lst
        
    def text(self):
        space_object = widgets.Text(
                value="",
                description="Target Object/Target Coordinates",
                continuous_update=True,
                layout=widgets.Layout(flex='1 1 auto', width='auto'),
                style={'description_width': '31.5%'})
        display(space_object)
        
class TableNotExistError(Exception):
    pass
