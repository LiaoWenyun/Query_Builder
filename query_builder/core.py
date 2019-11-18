import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output


__all__ = ['QueryBuilder']


class QueryBuilder:
    
    def __init__(self):
        self.query_output = ''
        self.column_type_dictionary ={}
        self.condition_list = []
        self.out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_builder()
        
    
    def query_builder(self):
        self.__get_service()
        
    def __get_service(self):
        service_combobox_list = ['https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap/',
                                'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/youcat/',
                                'https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/']
        self.delete_button = widgets.Button(
            description="Delete",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70px'))
        self.delete_button.on_click(self.__button_clicked)
        
        self.query_button = widgets.Button(
            description="Query",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70PX'))
        self.query_button.on_click(self.__query_clicked)
        
        self.clear_button = widgets.Button(
            description="Clear",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70px'))
        self.clear_button.on_click(self.__button_clicked)
        self.clear_button.click()
        self.buttons_ui = widgets.VBox([self.delete_button,
                                        self.clear_button,
                                        self.query_button],
                                       layout=widgets.Layout(top='8px',
                                                             height='90px',
                                                             width='100px'))
        self.output_ui = widgets.HBox([self.out, self.buttons_ui])

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
        
        display(self.query_out, self.service_combobox, self.tables, self.output_ui)

    
    def __get_table(self, service):
        try:
            self.service = pyvo.dal.TAPService(service)
            table_query = "SELECT table_name FROM tap_schema.tables"
            tables = self.service.search(table_query)
            table_list = [x.decode() for x in list(tables['table_name'])]
        except Exception:
            print("Service not found")
            self.output_ui.layout.visibility = 'hidden' 
            return
        self.output_ui.layout.visibility = 'visible'
        self.tables_dropdown = widgets.Dropdown(
            options=table_list,
            description='Table',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        self.columns = widgets.interactive_output(
            self.__get_columns,
            {'table': self.tables_dropdown})
        display(self.tables_dropdown, self.columns)
       
    def __get_columns(self, table):
        columns = self.__get_column_list(table)
        self.column_name = widgets.Dropdown(
            options=columns,
            description='column',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        self.other_fields = widgets.interactive_output(
            self.__get_other_fields,
            {'column': self.column_name})
        column_output_box = widgets.HBox([widgets.Box([self.column_name],
                                                      layout=widgets.Layout(width="50%")),
                                          widgets.Box([self.other_fields],
                                                      layout=widgets.Layout(top="-6px",
                                                                            width="50%"))])
        display(column_output_box)
    
    def __get_other_fields(self, column):
        if self.column_type_dictionary[column] == 'char':
            method_list = ['like', 'equal']
        else:
            method_list = ['>', '<', '>=', '<=', '=']
            
        self.method = widgets.Dropdown(
            options=method_list,
            description='')
        
        self.column_value = widgets.Text(
            value='',
            placeholder='value',
            description='')
        
        self.add_button = widgets.Button(
            description="",
            icon='plus',
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.add_button.on_click(self.__button_clicked)
        
        ui = widgets.HBox([self.method,
                           self.column_value,
                           self.add_button],
                          layout=widgets.Layout(width='100%'))
        display(ui)
        
    def __get_column_list(self, table):
        query = f"""SELECT column_name, datatype from
        tap_schema.columns WHERE table_name = '{table}'"""
        output = self.service.search(query)
        column_lst = [x.decode() for x in list(output['column_name'])]
        type_lst = [x.decode() for x in list(output['datatype'])]
        for i in range(0, len(column_lst)):
            self.column_type_dictionary[column_lst[i]] = type_lst[i]
        return column_lst
        
        
    def __query_clicked(self, b):
        with self.query_out:
            clear_output()
            query = self.get_query()
            self.query_output = self.service.search(query)


    def get_query_result(self, output_format='votable'):
        if self.query_output != '':
            if(output_format=='pandas'):
                return self.query_output.table.to_pandas()
            elif(output_format=='votable'):
                return self.query_output.table
        else:
            return
        
            
    def get_query(self):
        Query = f"SELECT * FROM {self.tables_dropdown.value}"
        if len(self.condition_list) > 0:
            Query += " WHERE ("
        for item in self.condition_list:
            item = item.split(" ")
            if item[1] == 'like' :
                Query += f" AND {item[0]} " + f"{item[1]} " + f"'%{str(item[2])}%'"
            elif item[1] == 'equal' :
                Query += f" AND {item[0]}" + f"=" + f"'{str(item[2])}'"
            elif self.column_type_dictionary[item[0]] == 'int':
                Query += f" AND {item[0]}" + f"{item[1]}" + f"{int(item[2])}"                
            elif self.column_type_dictionary[item[0]] == 'double':
                Query += f" AND {item[0]}" + f"{item[1]}" + f"{float(item[2])}"
        Query += ")"
        Query = Query.replace("WHERE ( AND", "WHERE (")
        print(f"Query: {Query}")
        return Query
    
    
    
    def __button_clicked(self, b):
        with self.out: 
            clear_output()
            if b.description == 'Delete':
                if len(self.condition_list) > 0:
                    self.condition_list.remove(self.conditions.value)
            elif b.description == 'Clear':
                self.condition_list = []
            else:
                condition_item = f"""
                {self.column_name.value}
                {self.method.value}
                {self.column_value.value}"""
                
                self.condition_list.append(condition_item)
            
            self.conditions = widgets.Select(
                    options=self.condition_list,
                    layout=widgets.Layout(flex='1 1 auto', width='auto'),
                    description='')    
            ui_condition = widgets.HBox([self.conditions])    
            display(ui_condition)
        
      
        