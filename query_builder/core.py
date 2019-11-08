import ipywidgets as widgets
from IPython.display import display
from IPython.display import Image, display, clear_output

__all__ = ['QueryBuilder']


class QueryBuilder():

    def __init__(self):
        print("ADQL Builder")
        self.dropdown_list = ['1', '2','3']
        self.combobox_list = ['a','b','c']
        self.method_list = ['equal', 'like', 'contain']
        self.condition_list =[]
        self.search_output = widgets.Output()
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
        
        self.column_value = widgets.Combobox(
            value='',
            placeholder='value',
            options=self.combobox_list,
            description='',
            layout=widgets.Layout(flex='1 1 auto',
                                  width='auto'),
            style={'description_width': 'initial'})
        
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
        
        self.search_button = widgets.Button(
            description="Search",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70PX'))
        self.search_button.on_click(self._search_clicked)
        
        self.clear_button = widgets.Button(
            description="Clear",
            icon='',
            style=widgets.ButtonStyle(button_color='#E58975'),
            layout=widgets.Layout(height = "25px",
                                  width='70px'))
        self.clear_button.on_click(self._button_clicked)
        self.clear_button.click()
        self.ui = widgets.HBox([self.column_name, self.method, self.column_value, self.add_button])
        self.buttons_ui = widgets.VBox([self.delete_button, self.clear_button, self.search_button],layout=widgets.Layout(top = '8px'))
        self.output_ui = widgets.HBox([self.out, self.buttons_ui])
            
    def adql_builder(self):
        display(self.ui, self.output_ui, self.search_output)
    
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
            
    def _search_clicked(self,b):
        with self.search_output:
            clear_output()
            print(self.condition_list)

        
        
    def text(self):
        space_object = widgets.Text(
                value="",
                description="Target Object/Target Coordinates",
                continuous_update=True,
                layout=widgets.Layout(flex='1 1 auto', width='auto'),
                style={'description_width': '31.5%'})
        display(space_object)
