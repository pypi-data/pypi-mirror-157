import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_notebook
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.express as px
from statistics import mean
output_notebook()

class Report:
    def shortreport(df):
        out1 = widgets.Output()
        out2 = widgets.Output()
        out3 = widgets.Output()
        out4 = widgets.Output()
    
        tab = widgets.Tab(children = [out1, out2, out3, out4])
        tab.set_title(0, 'Dataset_report')
        tab.set_title(1, 'Interaction')
        tab.set_title(2, 'Correlation')
        tab.set_title(3, 'Boxplot')
        display(tab)

        with out1:
        
            def dataset_report(df):
                print('\033[1m' +"\t\t\t\t\tData report")
                print("Number of columns: ",df.shape[1])
                print("Number of rows: ",df.shape[0])
                print("types of columns with numbers; ")
                a = df.dtypes.value_counts()
                print(a)
                
                def var_dropdown(x):
        
                    features(x_dropdown.children[0].value,df)
                    p = create_figure(x_dropdown.children[0].value, df)
                    with output_figure:
                        clear_output(True)    
                    return x
                def features(x_var,df):
                    miss = df[x_var].isnull().sum()
                    miss_p = df[x_var].isnull().sum() * 100 / len(df[x_var])
                    miss_percent = "{:.2f}".format(miss_p)
                    zero_p = df[x_var].isin([0]).sum()* 100 / len(df[x_var])
                    zeros_percent = "{:.2f}".format(zero_p)
                    if (df[x_var].dtype.name == ('object')):
                        print('\033[1m' + "Data Type\t:", df[x_var].dtype.name)
                        print('\033[1m' + "Distinct Values\t:",df[x_var].nunique())
            
                        if miss_p >=5.00:
                            print('\033[91m' + 'Missing Values\t:',miss)
                            print('\033[91m' + "Missing Values %:",miss_percent,"%")
                        else:
                            print('\033[1m' + "Missing Values\t:",miss)
                            print('\033[1m' + "Missing Values %:",miss_percent,"%")
                        print('\033[92m' + "Zeros\t: NA")
                    else:
                        print('\033[1m' + "Data Type\t:", df[x_var].dtype.name)
                        print( "Mean\t:", mean(df[x_var]))
                        print( "Standard Deviation\t:", np.std(df[x_var]))
                        
                        print( "Distinct Values\t:",df[x_var].nunique())
                        print( "Minimum\t:",np.min(df[x_var]))
                        print( "Maximum\t:",np.max(df[x_var]))
            
                        if zero_p>5.00:
                            print('\033[91m' + "Zeros\t: "+ str(df[x_var].isin([0]).sum())+ '\033[0m')
                            print('\033[1m'+'\033[91m' + "Zeros %\t: " + str(zeros_percent) + '\033[0m')
                        else:
                            print('\033[1m' + "Zeros\t:",df[x_var].isin([0]).sum())
                            print('\033[1m' + "Zeros %\t:",zeros_percent,'%')
                        if miss_p >=5.00:
                
                            print('\033[91m' + "Missing Values\t:"+str(miss)+ '\033[0m')
                            print('\033[91m' + "Missing Values %:"+str(miss_percent)+"%"+'\033[0m')
                        else:
                            print('\033[1m' + "Missing Values\t:",miss)
                            print('\033[1m' + "Missing Values %:",miss_percent,"%")
                
                    output_figure = widgets.Output()
                def create_figure(x_var, df):
            
                    fig = px.histogram(df, x=x_var, width=1000,)
                    fig.show()
        
                output_figure = widgets.Output()

                x_dropdown = widgets.interactive(var_dropdown, x= df.columns)
                x_dropdown.children[0].description = 'Features: '
                x_dropdown.children[0].value = df.columns[0]

                menu = widgets.VBox([x_dropdown])

                app_layout = widgets.Layout(
                    display='flex',
                    flec_flow='row nowrap',
                    align_items='center',
                    border = 'none',
                    width ='100%',
                    margin ='5px 5px 5px 5px')

                app = widgets.Box([menu, output_figure], layout= app_layout)
                display(app)
        
            dataset_report(df)

        with out2:
            def interaction_report(df):
                new_df= pd.DataFrame()
                numerical_col=[]
                for i in df.columns:
                    if (df[i].dtype.name == ('object')):
                        continue
                    else:
                        numerical_col.append(i)
                for i in numerical_col:
                    new_df[i] = df[i]
                for i in new_df:
                    if new_df[i].nunique() == len(new_df[i]):
                        new_df = new_df.drop(columns=[i])
                
            
                def var_dropdown(x):
                    p = create_figure(x_dropdown.children[0].value, y_dropdown.children[0].value, new_df)
                    fig[0] = p
                    with output_figure:
                        clear_output(True)
                        fig[0].show()
                    fig[0]=p
                    return x
                def create_figure(x_var,y_var, new_df):
                    p = px.scatter(new_df, x = x_var ,y=y_var, width=700, height=700)
                    return p
                fig= []
                p = create_figure(numerical_col[0],numerical_col[1],df)
                fig.append(p)

                output_figure = widgets.Output()
                with output_figure:
                    show(fig[0])
                output_figure = widgets.Output()
                x_dropdown = widgets.interactive(var_dropdown, x= new_df.columns)
                x_dropdown.children[0].description = 'x-axis'
                x_dropdown.children[0].value = new_df.columns[0]
                
                y_dropdown = widgets.interactive(var_dropdown, x= new_df.columns)
                y_dropdown.children[0].description = 'y-axis'
                y_dropdown.children[0].value = new_df.columns[1]
                layout = widgets.Layout(display='flex',
                                        flex_flow='column',
                                        width='40%')

                menu = widgets.VBox([x_dropdown, y_dropdown],layout=layout)

                app_layout = widgets.Layout(
                    display='flex',
                    flec_flow='row nowrap',
                    align_items='center',
                    border = 'none',
                    width ='100%',
                    margin ='2px 2px 2px 2px')
                app = widgets.Box([menu, output_figure], layout= app_layout)

                display(app)
            interaction_report(df)
        with out3:
            def check_correlation(df):
                corr_matrix = df.corr()
                fig = px.imshow(corr_matrix)
                fig.show()
            check_correlation(df)
        with out4:
            def outlier(df):
                new_df= pd.DataFrame()
                numerical_col=[]
                for i in df.columns:
                    if (df[i].dtype.name == ('object')):
                        continue
                    else:
                        numerical_col.append(i)
                for i in numerical_col:
                    new_df[i] = df[i]
                for i in new_df:
                    if new_df[i].nunique() == len(new_df[i]):
                        new_df = new_df.drop(columns=[i])
                def var_dropdown(x):
                    p = create_figure(x_dropdown.children[0].value, new_df)
                    
                    with output_figure:
                        clear_output(True)
                    return x
                def create_figure(x_var, new_df):
                    fig = px.box(new_df, y=x_var, width=1000, height=700)
                    fig.show()
                output_figure = widgets.Output()
                x_dropdown = widgets.interactive(var_dropdown, x= new_df.columns)
                x_dropdown.children[0].description = 'x-axis'
                x_dropdown.children[0].value = new_df.columns[0]
                menu = widgets.VBox([x_dropdown])

                app_layout = widgets.Layout(
                    display='flex',
                    flec_flow='row nowrap',
                    align_items='center',
                    border = 'none',
                    width ='100%',
                    margin ='2px 2px 2px 2px')
                app = widgets.Box([menu, output_figure], layout= app_layout)

                display(app)
            outlier(df)
    