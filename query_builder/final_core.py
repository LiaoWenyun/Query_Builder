import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output

__all__ = ['QueryBuilder']

class QueryBuilder:
    def __init__(self):
        
        self.list_of_join_tables = []
        self.schema_table_dictionary = {}
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out.layout.border = "1px solid green"        
        self.view_query_button = widgets.Button(
            description="View Query",
            layout=widgets.Layout(width='100px'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.view_query_button.on_click(self.__display_query)
        display(widgets.HBox([self.view_query_button, self.query_out]))
        
        self.service_combobox = widgets.Combobox(
            value='https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/',
            options=[],
            description='Service',
            continuous_update=False,
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
        self.schema_dropdown = widgets.Dropdown(
            options=[],
            description='Schema',
            continuous_update=False,
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'))
        
        self.table_one = widgets.Dropdown(
            options=[],
            description='Table',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
        self.join_button = widgets.Button(
            description="ADD",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.join_button.on_click(self.__add_button_clicked)

    def Start_query(self):
        self.__get_service()
        
    
    def __get_service(self):
        service_combobox_list = ['https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap/',
                                 'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/youcat/',
                                 'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/']
        
        self.service_combobox.options = service_combobox_list 
        output_schema = widgets.interactive_output(
            self.__get_schema,
            {'service': self.service_combobox})
        display(self.service_combobox, output_schema)


    def __get_schema(self, service):
        try:
            self.service = pyvo.dal.TAPService(service)
            table_query1 = "SELECT schema_name FROM tap_schema.schemas"
            table_query2 = "SELECT schema_name, table_name FROM tap_schema.tables"
            schemas = self.service.search(table_query1)
            tables = self.service.search(table_query2)
            schema_list = [x.decode() for x in list(schemas['schema_name'])]
            table_schema_list = [x.decode() for x in list(tables['schema_name'])]
            table_list = [x.decode() for x in list(tables['table_name'])]
            for idx in range(0, len(table_schema_list)):
                self.schema_table_dictionary[table_list[idx]] = table_schema_list[idx]
        except Exception:
            print("Service not found")
            return
        self.schema_dropdown.options = schema_list
        output_tables = widgets.interactive_output(
            self.__get_table,
            {'schema': self.schema_dropdown})
        display(self.schema_dropdown, output_tables)

 
    def __get_table(self, schema):
        table_list = []
        for key, value in self.schema_table_dictionary.items():
            if value == schema:
                table_list.append(key)
        
        self.table_one.options=table_list

        self.list_of_join_tables.append(widgets.HBox([self.table_one, self.join_button]))
        self.table_text = widgets.Text(value=self.list_of_join_tables[0].children[0].value, description='')
        display(self.list_of_join_tables[0])
        
        
    def __display_query(self, b):
        with self.query_out:
            clear_output()
            for item in self.list_of_join_tables:
                self.query_body = f"""SELECT \n * \nFROM \n{item.children[0].value}"""
            print(self.query_body)
    
    
    def __add_button_clicked(self, b):
        val=0



    def __edit_button_clicked(self, b):
        val=0
    def __disable_fields(self, set_disable):
        val=0
    def __search_button_clicked(self, b):
        val=0
    def __clear_button_clicked(self, b):
        val=0
    def __display_button_clicked(self, b):
        val=0
        
