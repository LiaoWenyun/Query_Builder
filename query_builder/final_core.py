import pandas
import ipywidgets as widgets
import pyvo
from IPython.display import Image, display, clear_output
import networkx as nx

__all__ = ['QueryBuilder']

class QueryBuilder:
    def __init__(self):
        self.c =0  ########################used for testing, need to remove later 
        self.list_of_join_tables = []
        self.count = 0
        self.schema_table_dictionary = {}
        self.joinable_dictionary = {}
        self.on_condition_dictionary = {}
        self.column_type_dictionary ={}
        self.graph = nx.Graph()
        self.query_out = widgets.Output(layout=widgets.Layout(width='100%'))
        self.add_button_output = widgets.Output(layout=widgets.Layout(width='100%'))
        self.where_condition_out = widgets.Output(layout=widgets.Layout(width='100%'))
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
        
        self.column_dropdown = widgets.Dropdown(
            options=[],
            description='Columns',
            continuous_update=False,
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'))
        

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
        display(widgets.HBox([self.service_combobox, self.schema_dropdown]))
        display(output_schema)

    def __get_schema(self, service):
        try:
            self.joinable_dictionary = {}
            self.on_condition_dictionary = {}
            self.service = pyvo.dal.TAPService(service)
            table_query1 = "SELECT schema_name FROM tap_schema.schemas"
            table_query2 = "SELECT schema_name, table_name FROM tap_schema.tables"
            table_query3 = "SELECT from_table,target_table,from_column,target_column FROM tap_schema.keys JOIN tap_schema.key_columns ON tap_schema.keys.key_id=tap_schema.key_columns.key_id"
            schemas = self.service.search(table_query1)
            tables = self.service.search(table_query2)
            joinables = self.service.search(table_query3)
            schema_list = [x.decode() for x in list(schemas['schema_name'])]
            table_schema_list = [x.decode() for x in list(tables['schema_name'])]
            table_list = [x.decode() for x in list(tables['table_name'])]
            from_table_list = [x.decode() for x in list(joinables['from_table'])]
            target_table_list = [x.decode() for x in list(joinables['target_table'])]
            from_column_list = [x.decode() for x in list(joinables['from_column'])]
            target_column_list = [x.decode() for x in list(joinables['target_column'])]
            for idx in range(0, len(table_schema_list)):
                self.schema_table_dictionary[table_list[idx]] = table_schema_list[idx]
            for idx in range(0,len(from_table_list)):
                relationship1 = f"{from_table_list[idx]} to {target_table_list[idx]}"
                relationship2 = f"{target_table_list[idx]} to {from_table_list[idx]}"
                on_condition1 = f"{from_table_list[idx]}.{from_column_list[idx]}={target_table_list[idx]}.{target_column_list[idx]}"
                on_condition2 = f"{target_table_list[idx]}.{target_column_list[idx]}={from_table_list[idx]}.{from_column_list[idx]}"
                if relationship1 not in self.on_condition_dictionary: 
                    self.on_condition_dictionary[relationship1] = on_condition1
                if relationship2 not in self.on_condition_dictionary: 
                    self.on_condition_dictionary[relationship2] = on_condition2
            #### joinable_dictionary is the graph which be used in the BFS later on
            for table in table_list:
                self.joinable_dictionary[table] = []
            for idx in range(0,len(from_table_list)):
                if target_table_list[idx] not in self.joinable_dictionary[from_table_list[idx]]:
                    self.joinable_dictionary[from_table_list[idx]].append(target_table_list[idx])
                    self.joinable_dictionary[target_table_list[idx]].append(from_table_list[idx])
            for key, value in self.joinable_dictionary.items():
                for value_item in value:
                    self.graph.add_edge(key, value_item)
        except Exception:
            print("Service not found")
            return
        self.schema_dropdown.options = schema_list
        output_tables = widgets.interactive_output(
            self.__get_table,
            {'schema': self.schema_dropdown})
        display(output_tables)

 
    def __get_table(self, schema):
        ## clear the join tables 
        self.list_of_join_tables = []
        self.add_button_output.clear_output()
        self.join_button.layout.visibility = 'visible'
        #####        
       
        table_list = []
        for key, value in self.schema_table_dictionary.items():
            if value == schema:
                table_list.append(key)
        
        self.table_one.options=table_list
        self.table_text = widgets.Text(value=f"table_name='{self.table_one.value}'", description='')  ### change this value to trigger columns
        ouput_columns = widgets.interactive_output(
            self.__get_select_columns,
            {'table_text':self.table_text})
        ouput_where_columns = widgets.interactive_output(
            self.__set_columns,
            {'table_text':self.table_text})
        widgets.interactive_output(
            self.__change_columns,
            {'table':self.table_one})
        display(widgets.HBox([self.table_one, self.join_button]),self.add_button_output, ouput_columns, ouput_where_columns)
        
        

    def __set_columns(self, table_text):   ########################
        self.tmp_where_condition_dictionary = {}
        self.list_of_where_object = {}   ##clear the list 
        self.button_to_trigger = widgets.Button(description = "update")
        self.button_to_trigger.on_click(self.__column_button_clicked)
        self.button_to_trigger.click()  ## trigger the button
        display(self.where_condition_out)
        
    def __get_other_fields(self, column, key):   ##########################
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
            
            
    def __column_button_clicked(self,b):  ########################
        print(f"button triggered  {self.c}" )   ########################## used for teating , need to remove later 
        self.c+=1                    ##############used to test how many time the button itself is triggere, when change a sechema it got triggered 3 times each time 
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
            
            #self.view_query_button.click()         
            
            
    def __change_columns(self, table):
        if len(self.list_of_join_tables) == 0:
            self.table_text.value = f"(table_name='{table}')"
        else:
            string = ""
            for idx in range(0, len(self.list_of_join_tables)):
                if idx == 0: 
                     string = f"(table_name='{self.list_of_join_tables[idx].children[0].value}'"
                else:
                    string = string + f" OR table_name='{self.list_of_join_tables[idx].children[0].value}'"
            string += ")"
            self.table_text.value = string

    def __get_where_columns(self, table_text):
        columns = self.__get_column_list(table_text)
        
        
    
    
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
        
        
    
    def __add_button_clicked(self, b):
        with self.add_button_output:
            clear_output()
            if len(self.list_of_join_tables) < 1:
                self.list_of_join_tables.append(widgets.HBox([self.table_one, self.join_button]))
                self.table_one.options= [self.table_one.value]
                self.join_button.layout.visibility = 'hidden' 
                
            join_table = widgets.Dropdown(
                options=self.__BFS(self.joinable_dictionary, self.list_of_join_tables[-1].children[0].value),
                description='Table',
                layout=widgets.Layout(flex='1 1 auto',
                                      width='auto'),
                style={'description_width': 'initial'})
            join_button = widgets.Button(
                description="ADD",
                icon='',
                style=widgets.ButtonStyle(button_color='#E58975'))
            join_button.on_click(self.__add_button_clicked)
            self.list_of_join_tables.append(widgets.HBox([join_table, join_button]))
            widgets.interactive_output(
                self.__change_columns,
                {'table':join_table})
            
            for table in self.list_of_join_tables[1:-1]:
                table.children[0].options= [table.children[0].value]
                table.children[1].layout.visibility = 'hidden'

            for x in self.list_of_join_tables[1:]:
                display(x)
 


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
        
        
    def __BFS(self, graph, selected_node):
        result = []
        visited = [False] * (len(graph))
        queue = []
        queue.append(selected_node)
        visited[list(graph.keys()).index(selected_node)] = True
        
        while queue:
            selected_node = queue[0]
            queue = queue[1:]
            result.append(selected_node)
        
            for i in graph[selected_node]:
                if visited[list(graph.keys()).index(i)] == False: 
                    queue.append(i)
                    visited[list(graph.keys()).index(i)] = True
        return result[1:]
        
        
        
    def __shortest_path(self, start, end):
        return nx.dijkstra_path(self.graph, start, end)
    
    
    def __display_query(self, b):
        with self.query_out:
            clear_output()
            tables =""
            used_tables = []
            for index in range(0, len(self.list_of_join_tables)):
                if index == 0:
                    tables = f" {self.list_of_join_tables[index].children[0].value}"
                    used_tables.append(self.list_of_join_tables[index].children[0].value)
                else:
                    previous_table = self.list_of_join_tables[index-1].children[0].value
                    current_table = self.list_of_join_tables[index].children[0].value
                    if current_table not in used_tables:
                        used_tables.append(current_table)
                        join_order = self.__shortest_path(previous_table, current_table)
                        for i in range(1, len(join_order)):
                            relationship = f"{join_order[i-1]} to {join_order[i]}" 
                            on_condition = self.on_condition_dictionary[relationship]
                            tables = tables + " JOIN " + join_order[i] +" ON " + on_condition +"\n"
                    else:
                        pass
            self.query_body = f"""SELECT \n * \nFROM \n{tables}"""
            print(self.query_body)
        
        