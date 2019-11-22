import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output


__all__ = ['QueryBuilder']


class QueryBuilder:
    def __init__(self):
        self.selected_on_field = [None]*5  # hardcode max join tables
        self.table_lst = []                # dropdown items for a table
        self.list_of_tables = []           # list of table objects
        self.list_of_on_object = []        # list of on_condition objects
        self.count = 0
        table_join_condition = {}        
        self.column_type_dictionary ={}
        self.condition_list = []
        self.table_join_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.where_condition_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out.layout.border = "1px solid green"
        self.view_query_button = widgets.Button(
            description="View Query",
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.view_query_button.on_click(self.__display_query)
        display(widgets.HBox([self.view_query_button, self.query_out]))
        self.__get_service()
        
        
    def __display_query(self, b):
        with self.query_out:
            clear_output()
            selected_tables = self.selected_tables
            for i in range (0,len(self.list_of_on_object)):
                string = f" JOIN {self.list_of_tables[i+1].value} ON {self.selected_on_field[i+1].value}" 
                selected_tables += string
            
            selected_columns = ""
            where_condition= ""
            if len(self.slect_multiple_columns.value) > 0:
                for item in self.slect_multiple_columns.value:
                    selected_columns += f" {item},"
            else:
                selected_columns = " * "
                
                
            for key in self.list_of_where_object.keys():
                item1 = self.list_of_where_object[key].children[0].children[0]
                tmp2 = self.tmp_where_condition_dictionary[key].children[0].value
                tmp3 = self.tmp_where_condition_dictionary[key].children[1].value
                item2 = tmp2
                item3 = tmp3
                if tmp2 == 'like':
                    item3 = f"'%{tmp3}%'"
                elif tmp2 == 'equal':
                    item2 = '='
                    item3 = f"'{tmp3}'"

                where_condition += f" {item1.description} {item1.value} {item2} {item3} "
                
            query_body = f"""SELECT{selected_columns[:-1]} FROM {selected_tables} {where_condition}"""
            display(query_body)
    
    
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
        display(self.service_combobox, self.tables)
        
        
    def __get_table(self, service):
        try:
            self.service = pyvo.dal.TAPService(service)
            table_query = "SELECT table_name FROM tap_schema.tables"
            tables = self.service.search(table_query)
            self.table_list = [x.decode() for x in list(tables['table_name'])]
        except Exception:
            print("Service not found")
            return
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
        self.table_text = widgets.Text(value= self.list_of_tables[0].value,
                                       description='')
        self.columns_select = widgets.interactive_output(self.__get_select_columns, {'table_text': self.table_text})
        self.columns = widgets.interactive_output(self.__set_columns, {'table_text': self.table_text})
        self.trigger_column = widgets.interactive_output(self.__trigger_column_widget, {'table': self.tables_dropdown})
        display(widgets.HBox([self.tables_dropdown, self.join_button]), self.table_join_out, self.columns_select, self.columns)
        
    
                                                         
    def __trigger_column_widget(self, table):
        self.selected_tables = table
        string = f"(table_name='{self.list_of_tables[0].value}' "
        for x in range(1,len(self.list_of_tables)):
            string = string + f"OR table_name='{self.list_of_tables[x].value}' "
        string = string + ")"
        self.table_text.value = string
        
    def __get_select_columns(self, table_text):
        columns = self.__get_column_list(table_text)
        self.slect_multiple_columns = widgets.SelectMultiple(
            options = columns,
            description='SELECT ',
            disabled=False)
        display(self.slect_multiple_columns)
        
        
    def __get_column_list(self, table_text):
        query = f"""SELECT column_name, datatype from
        tap_schema.columns WHERE """
        query = query + table_text
        output = self.service.search(query)
        column_lst = [x.decode() for x in list(output['column_name'])]
        type_lst = [x.decode() for x in list(output['datatype'])]
        for i in range(0, len(column_lst)):
            self.column_type_dictionary[column_lst[i]] = type_lst[i]
        return column_lst

    
    def __set_columns(self, table_text):
        self.tmp_where_condition_dictionary = {}
        self.list_of_where_object = {}   ##clear the list 
        self.button_to_trigger = widgets.Button(description = "update")
        self.button_to_trigger.on_click(self.__column_button_clicked)
        self.button_to_trigger.click()  ## trigger the button
        display(self.where_condition_out)
        
    
    def __get_other_fields(self, column, key):
        if self.column_type_dictionary[column] == 'char':
            method_list = ['like', 'equal']
        else:
            method_list = ['>', '<', '>=', '<=', '=', 'between']
            
        self.method = widgets.Dropdown(
            options=method_list,
            description='')
        
        self.column_value = widgets.Text(
            value='',
            placeholder='value',
            description='')
        
        method_ui = widgets.HBox([self.method,
                                  self.column_value],
                                 layout=widgets.Layout(width='100%'))
        self.tmp_where_condition_dictionary[key] = method_ui
        display(method_ui)



    def __column_button_clicked(self,b):
        with self.where_condition_out:
            clear_output()
            columns = self.__get_column_list(self.table_text.value)
            if (b.description == '+' or b.description == 'update'):
                description = 'WHERE'
                if len(self.list_of_where_object) != 0:
                    b.description = '-'
                    description = 'AND'
                self.create_new_flag = 1
                column_name = widgets.Dropdown(
                    options=columns,
                    description=description,
                    layout=widgets.Layout(flex='1 1 auto',
                                          width='auto'),
                    style={'description_width': 'initial'})
                save_key = widgets.Text(value=str(self.count)
                                        ,description='Key')
                other_fields = widgets.interactive_output(
                    self.__get_other_fields, {'column': column_name, 'key':save_key})
                add_button = widgets.Button(description="+",
                                                     icon='',
                                                     tooltip=str(self.count),
                                                     style=widgets.ButtonStyle(button_color='#E58975'))
                add_button.on_click(self.__column_button_clicked)
                column_output_box = widgets.HBox([widgets.Box([column_name],
                                                              layout=widgets.Layout(width="45%")),
                                                  widgets.Box([other_fields],
                                                              layout=widgets.Layout(top="-6px",width="45%")),
                                                  widgets.Box([add_button],
                                                              layout=widgets.Layout(width="10%"))])
                self.list_of_where_object[str(self.count)] = column_output_box
                self.count += 1
                
            elif (b.description == '-'): 
                del self.list_of_where_object[b.tooltip]
                list(self.list_of_where_object.values())[0].children[0].children[0].description = 'WHERE'
                del self.tmp_where_condition_dictionary[b.tooltip]

            for key in self.list_of_where_object.keys():
                display(self.list_of_where_object[key])
        
    def __join_button_clicked(self,b):
        with self.table_join_out:
            clear_output()
            
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
                
            if b.description == "JOIN":
                self.join_button.layout.visibility = 'hidden' 
                new_tables_dropdown = widgets.Dropdown(
                    options=self.table_list,
                    description='Table',
                    layout=widgets.Layout( width='600px'),
                    style={'description_width': 'initial'})
                self.list_of_tables.append(new_tables_dropdown)   #add into list of table object
                #######use a Int widget to store the index
                save_index = widgets.IntText(
                    value=len(self.list_of_tables)-1,
                    description='Any:')
           
                on_condition = widgets.interactive_output(self.get_on_field,
                                                         {'dropdown1':self.list_of_tables[-2],
                                                          'dropdown2':self.list_of_tables[-1],
                                                          'index':save_index})
                on_object_ui = widgets.HBox([ widgets.Box([self.list_of_tables[-1]],
                                                          layout=widgets.Layout(width="40%")),
                                              widgets.Box([on_condition],
                                                          layout=widgets.Layout(top="-6px",width="60%"))])
                                                          
                self.list_of_on_object.append(on_object_ui)     #add into on condition object
            elif b.description == "REMOVE":
                self.list_of_tables.pop()
                self.list_of_on_object.pop()
                self.selected_on_field.pop()
                #### change the column field list
                string = f"(table_name='{self.list_of_tables[0].value}' "
                for x in range(1,len(self.list_of_tables)):
                    string = string + f"OR table_name='{self.list_of_tables[x].value}' "
                string = string + ")"
                self.table_text.value = string
                ####
           
            for x in self.list_of_on_object[:-1]:
                display(x)
            if len(self.list_of_on_object)!= 0:
                table_object = widgets.HBox([self.list_of_on_object[-1], new_join_button, new_remove_button])
                display(table_object)
            else:
                self.join_button.layout.visibility = 'visible'
                
    def get_on_field(self, dropdown1, dropdown2, index):
        lst_items = []
        table_query = f"""SELECT from_table, from_column,target_table,
        target_column FROM tap_schema.keys JOIN tap_schema.key_columns ON
        tap_schema.keys.key_id = tap_schema.key_columns.key_id WHERE
        ( from_table='{dropdown1}' AND target_table='{dropdown2}') OR
        ( from_table='{dropdown2}' AND target_table='{dropdown1}')""" 
        On_items = self.service.search(table_query)
        lst_from = [x.decode() for x in list(On_items['from_table'])]
        lst_from_column = [x.decode() for x in list(On_items['from_column'])]
        lst_target = [x.decode() for x in list(On_items['target_table'])]
        lst_target_column = [x.decode() for x in list(On_items['target_column'])]
        options = [f"""{lst_from[i]}.{lst_from_column[i]} == {lst_target[i]}.{lst_target_column[i]}""" for i in range(0,len(lst_from))]

        options_dropdown = widgets.Dropdown(
                    options=options,
                    description='ON',
                    layout=widgets.Layout( width='1500px'))
        self.selected_on_field[index] = options_dropdown

        #### change the column field list 
        if (len(options))>0:
            string = f"(table_name='{self.list_of_tables[0].value}' "
            for x in range(1,len(self.list_of_tables)):
                string = string + f"OR table_name='{self.list_of_tables[x].value}' "
            string = string + ")"
            self.table_text.value = string

        display(widgets.HBox([options_dropdown]),layout=widgets.Layout(width='100%'))
        

               

        
       