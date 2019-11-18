import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output


__all__ = ['QueryBuilder']


class QueryBuilder:
    def __init__(self):
        self.table_lst = [] #dropdown items for a table
        self.list_of_tables = []  # list of table objects
        self.list_of_on_object = []
        table_join_condition = {}
        self.table_join_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.__get_service()
    
    
    def __get_service(self):
        service_combobox_list = ['https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap/',
                                'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/youcat/',
                                'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/']


        self.service_combobox = widgets.Combobox(
            value='https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/',
            placeholder='',
            options=service_combobox_list,
            description='Service',
            continuous_update=False,
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
        self.tables = widgets.interactive_output(
            self.__get_table,
            {'service': self.service_combobox})
        
        display( self.query_out, self.service_combobox, self.tables)
        
        
    def __get_table(self, service):
        try:
            self.service = pyvo.dal.TAPService(service)
            table_query = "SELECT table_name FROM tap_schema.tables"
            tables = self.service.search(table_query)
            self.table_list = [x.decode() for x in list(tables['table_name'])]
        except Exception:
            print("Service not found")
            #self.output_ui.layout.visibility = 'hidden' 
            return
        #self.output_ui.layout.visibility = 'visible'
        self.tables_dropdown = widgets.Dropdown(
            options=self.table_list,
            description='Table',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        self.join_button = widgets.Button(
            description="JOIN",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.join_button.on_click(self.__join_button_clicked)
        self.list_of_tables.append(self.tables_dropdown)
        display(self.tables_dropdown, self.join_button, self.table_join_out)
    
    
    def __join_button_clicked(self,b):
        with self.table_join_out:
            clear_output()
            if b.description == "JOIN":
                self.join_button.layout.visibility = 'hidden' 
                new_tables_dropdown = widgets.Dropdown(
                    options=self.table_list,
                    description='Table',
                    layout=widgets.Layout(flex='1 1 auto',
                                          width='auto'),
                    style={'description_width': 'initial'})
                self.list_of_tables.append(new_tables_dropdown)   #add into list of table object
                on_condition = widgets.interactive_output(self.get_on_field,
                                                         {'dropdown1':self.list_of_tables[-2],
                                                          'dropdown2':self.list_of_tables[-1] })
                on_object_ui = widgets.HBox([new_tables_dropdown, on_condition])
                new_join_button = widgets.Button(
                    description="JOIN",
                    icon='',
                    style=widgets.ButtonStyle(button_color='#E58975'))                
                
                new_remove_button = widgets.Button(
                    description="REMOVE",
                    icon='',
                    style=widgets.ButtonStyle(button_color='#E58975'))
                new_join_button.on_click(self.__join_button_clicked)
                new_remove_button.on_click(self.__join_button_clicked)
                
                table_object = widgets.HBox([new_tables_dropdown, on_condition,new_join_button, new_remove_button])
                for x in self.list_of_on_object:
                    display(x)
                    
                display(table_object)
                self.list_of_on_object.append(on_object_ui)     #add into on condition object
            elif b.description == "REMOVE":
                
                display("")
        
    def get_on_field(self, dropdown1, dropdown2):    ##need to finish here 
        lst_items = []
        table_query = f"""SELECT from_table, from_column,target_table,target_column FROM tap_schema.keys JOIN tap_schema.key_columns on tap_schema.keys.key_id = tap_schema.key_columns.key_id WHERE ( from_table='{dropdown1}' AND target_table='{dropdown2}'""" 
        On_items = self.service.search(table_query)
        lst_from = [x.decode() for x in list(On_items['from_table'])]
        lst_target = [x.decode() for x in list(On_items['target_table'])]
        from_dropdown = widgets.Dropdown(
                    options=lst_from,
                    description='from',
                    layout=widgets.Layout(flex='1 1 auto',
                                          width='auto'),
                    style={'description_width': 'initial'})
        target_dropdown = widgets.Dropdown(
                    options=lst_from,
                    description='target',
                    layout=widgets.Layout(flex='1 1 auto',
                                          width='auto'),
                    style={'description_width': 'initial'})
        display(from_dropdown, target_dropdown)
        
        
        
        
       