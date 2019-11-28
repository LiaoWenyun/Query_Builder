import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output


__all__ = ['QueryBuilder']


class QueryBuilder:
    def __init__(self):
        self.selected_on_field = [None]*20  # hardcode max join tables
        self.table_lst = []                 # dropdown items for a table
        self.list_of_tables = []            # list of table objects
        self.list_of_on_object = []         # list of on_condition objects
        self.count = 0
        self.count_num_clicks = 0
        table_join_condition = {}        
        self.column_type_dictionary = {}
        self.description_dictionary = {}
        self.condition_list = []
        self.query_body = ""
        self.table_join_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.where_condition_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.query_out.layout.border = "1px solid green"
        self.edit_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.result = widgets.Output(layout=widgets.Layout(width='100%'))
        self.view_query_button = widgets.Button(
            description="View Query",
            layout=widgets.Layout(width='100px'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.view_query_button.on_click(self.__display_query)
        display(widgets.HBox([self.view_query_button, self.query_out]))
        self.clear_button = widgets.Button(
            description="CLEAR",
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.clear_button.on_click(self.__clear_button_clicked)
        self.search_button = widgets.Button(
            description="SEARCH",
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.search_button.on_click(self.__search_button_clicked)
        self.edit_button = widgets.Button(
            description="EDIT QUERY",
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style=widgets.ButtonStyle(button_color='#E58975'))
        self.edit_button.on_click(self.__edit_button_clicked)
        self.tmp_query = widgets.Textarea(
                description="",
                value="",
                layout=widgets.Layout(flex='1 1 auto',
                                      width='auto',
                                      height='100%'))
        self.tmp_query.layout.visibility = 'hidden'
        self.__get_service()
        display(widgets.HBox([self.clear_button, self.edit_button, self.search_button]))
        display(widgets.VBox([self.tmp_query], layout=widgets.Layout(height='200px')))
        display(self.result)

        
    def __edit_button_clicked(self, b):
        with self.edit_out:
            clear_output()
            self.count_num_clicks += 1
            if self.count_num_clicks%2 != 0:
                self.view_query_button.click()
                self.tmp_query.value = self.query_body
                self.__disable_fields(True)
                self.tmp_query.layout.visibility = 'visible'
            else:
                self.__disable_fields(False)
                self.tmp_query.layout.visibility = 'hidden'
    
    
    def __disable_fields(self, set_disable):
        self.view_query_button.disabled = set_disable
        self.service_combobox.disabled = set_disable
        for i in self.list_of_tables:
            i.disabled = set_disable
        for i in self.selected_on_field:
            if i != None:
                i.disabled = set_disable
        self.join_button.disabled = set_disable
        self.select_multiple_columns.disabled = set_disable
        if len(self.list_of_on_object) != 0:
            self.table_object.children[1].disabled = set_disable
            self.table_object.children[2].disabled = set_disable
        for i in list(self.list_of_where_object.values()):
            i.children[0].children[0].disabled = set_disable
        for i in list(self.list_of_where_object.values()):
            i.children[2].children[0].disabled = set_disable
        for i in list(self.tmp_where_condition_dictionary.values()):
            i.children[0].disabled = set_disable
        for i in list(self.tmp_where_condition_dictionary.values()):
            i.children[1].disabled = set_disable



    def __search_button_clicked(self, b):
        with self.result:
            clear_output()
            if self.tmp_query.value != "":
                result = self.service.search(self.tmp_query.value)
                display(result)
            else:
                display("Empty Query")
    
    
    def __clear_button_clicked(self, b):
        clear_output()
        self.__init__()
    
    
    def __display_query(self, b):
        with self.query_out:
            clear_output()
            Warn = ""
            selected_columns = ""
            where_condition= ""
            tmp_where_list = []
            used_table_list =[self.tables_dropdown.value]
            selected_tables = self.tables_dropdown.value + " \n"
            for i in range (0,len(self.list_of_on_object)):
                if self.selected_on_field[i+1].value != None:
                    if self.selected_on_field[i+1].value not in used_table_list:
                        string = f"JOIN {self.list_of_tables[i+1].value} ON {self.selected_on_field[i+1].value} \n"
                        selected_tables += string
                        used_table_list.append(self.selected_on_field[i+1].value)
                    else:
                        Warn = "Warning: Duplicated Table"
                        break
                else:
                    Warn = "Warning: On field can not be None"
                    break
            
            if len(self.select_multiple_columns.value) > 0:
                for item in self.select_multiple_columns.value:
                    if ' (indexed)' in item:
                        item = item.replace(' (indexed)', '')
                    selected_columns += f"{item}, \n"
            else:
                selected_columns = "* \n" 
          
            for key in self.list_of_where_object.keys():
                item1 = self.list_of_where_object[key].children[0].children[0].description
                item2 = self.list_of_where_object[key].children[0].children[0].value
                item3 = self.tmp_where_condition_dictionary[key].children[0].value
                item4 = self.tmp_where_condition_dictionary[key].children[1].value
                if item3 == 'like':
                    item4 = f"'%{item4}%'"
                elif item3 == 'equal':
                    item3 = '='
                    item4 = f"'{item4}'"
                if ' (indexed)' in item2:
                    item2 = item2.replace(' (indexed)', '')
          
                tmp_where_list.append([item1, item2, item3, item4])
            
            where_length = len(tmp_where_list)
            
            for index in range(0, where_length):
                if tmp_where_list[index][0] == "WHERE" and (tmp_where_list[index][3] == "''" or tmp_where_list[index][3] == "'%%'"):
                    if where_length >1:
                        tmp_where_list[index+1][0] == "WHERE"
                    
                elif tmp_where_list[index][0] == "AND" and (tmp_where_list[index][3] == "''" or tmp_where_list[index][3] == "'%%'"):
                    pass
                    
                else:
                    where_condition += f"{tmp_where_list[index][0]} {tmp_where_list[index][1]} {tmp_where_list[index][2]} {tmp_where_list[index][3]} \n"
                        
                
            self.query_body = f"""SELECT \n{selected_columns[:-1]} \nFROM \n{selected_tables}{where_condition}"""
            self.tmp_query.value = self.query_body
            print(self.query_body)
            print(Warn)
        
    
    
    
    
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
        #self.selected_tables = table
        string = f"(table_name='{self.list_of_tables[0].value}' "
        for x in range(1,len(self.list_of_tables)):
            string = string + f"OR table_name='{self.list_of_tables[x].value}' "
        string = string + ")"
        self.table_text.value = string
        
    def __get_select_columns(self, table_text):
        columns = self.__get_column_list(table_text)
        self.select_multiple_columns = widgets.SelectMultiple(
            options = columns,
            description='SELECT ',
            disabled=False,
            layout={'width':'500px'})
        display(self.select_multiple_columns)
        
        
    def __get_column_list(self, table_text):
        query = f"""SELECT column_name, table_name, indexed, datatype from
        tap_schema.columns WHERE """
        query = query + table_text
        output = self.service.search(query)
        column_lst = [x.decode() for x in list(output['column_name'])]
        table_name = [x.decode() for x in list(output['table_name'])]
        type_lst = [x.decode() for x in list(output['datatype'])]
        indexed_lst = output['indexed']
        for i in range(0, len(column_lst)):
            if indexed_lst[i] == 1:
                column_lst[i] = f"{table_name[i]}.{column_lst[i]} (indexed) "
            else: 
                column_lst[i] = f"{table_name[i]}.{column_lst[i]}"
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
            
            self.view_query_button.click()                    #################################
    
    
    
    def __join_button_clicked(self,b):
        with self.table_join_out:
            clear_output()
            
            new_join_button = widgets.Button(
                    description="JOIN",
                    icon='',
                    layout=widgets.Layout(width='100px'),
                    style=widgets.ButtonStyle(button_color='#E58975'))                
                
            new_remove_button = widgets.Button(
                    description="REMOVE",
                    icon='',
                    layout=widgets.Layout(width='170px'),
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
                widgets.interactive_output(self.__trigger_column_widget, {'table': new_tables_dropdown})
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
                self.table_object = widgets.HBox([self.list_of_on_object[-1], new_join_button, new_remove_button])
                display(self.table_object)
            else:
                self.join_button.layout.visibility = 'visible'
            self.view_query_button.click()                    #################################
                
    def get_on_field(self, dropdown1, dropdown2, index):
        lst_items = []
        table_query = f"""SELECT from_table, from_column,target_table,
        target_column, description FROM tap_schema.keys JOIN tap_schema.key_columns ON
        tap_schema.keys.key_id = tap_schema.key_columns.key_id WHERE
        ( from_table='{dropdown1}' AND target_table='{dropdown2}') OR
        ( from_table='{dropdown2}' AND target_table='{dropdown1}')""" 
        On_items = self.service.search(table_query)
        lst_from = [x.decode() for x in list(On_items['from_table'])]
        lst_from_column = [x.decode() for x in list(On_items['from_column'])]
        lst_target = [x.decode() for x in list(On_items['target_table'])]
        lst_target_column = [x.decode() for x in list(On_items['target_column'])]
        lst_description = [x.decode() for x in list(On_items['description'])]
        options = [f"""{lst_from[i]}.{lst_from_column[i]} == {lst_target[i]}.{lst_target_column[i]}""" for i in range(0,len(lst_from))]
        for idx in range(0, len(options)):
            self.description_dictionary[options[idx]] = f"Description: {lst_description[idx]}"
        
        options_dropdown = widgets.Dropdown(
                    options=options,
                    description='ON',
                    layout=widgets.Layout( width='400px'))
        description_output = widgets.interactive_output(self.__display_description, {"on_condition": options_dropdown})
        self.selected_on_field[index] = options_dropdown
        
        #### change the column field list 
        if (len(options))>0:
            string = f"(table_name='{self.list_of_tables[0].value}' "
            for x in range(1,len(self.list_of_tables)):
                string = string + f"OR table_name='{self.list_of_tables[x].value}' "
            string = string + ")"
            self.table_text.value = string

        display(widgets.VBox([options_dropdown, description_output]),layout=widgets.Layout(width='400px'))
        
    def __display_description(self, on_condition):
        if on_condition != None:
            display(self.description_dictionary[on_condition])
        
       