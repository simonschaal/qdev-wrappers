from qcodes.plots.pyqtgraph import QtPlot

import time

import qcodes as qc
from qcodes.dataset.data_set import load_by_id

from qcodes.dataset.data_export import (get_data_by_id, flatten_1D_data_for_plot,
                          get_1D_plottype, get_2D_plottype, reshape_2D_data,
                          _strings_as_ints)



class QtPlotbyID(QtPlot):
    
    
    def __init__(self, *args, id, refresh=1):
        
        super().__init__(*args)
        
        self.id = id
        
        alldata = get_data_by_id(self.id)
        self.nplots = len(alldata)

        # initiate plots
        for i, data in enumerate(alldata):
            
            x = data[0]
            y = data[1]
            
            if len(data) == 2:  # 1D PLOTTING

                po = self._add_1d(i, x, y)

            elif len(data) == 3:  # 2D PLOTTING

                z = data[2]

                po = self._add_2d(i, x, y, z)
                
            
        # add subscriber
        #dataset = load_by_id(self.id)
        #dataset.subscribe(self.update_from_subscriber, min_wait=0, min_count=1, state=[])
        
        dataset = load_by_id(self.id)
        self.completed = dataset.completed
        
        while not self.completed:
            dataset = load_by_id(self.id)
            self.completed = dataset.completed
            self.update_plots()
            time.sleep(refresh)
            
    
    
    def _add_1d(self, i, x, y):
        return self.add_to_plot(subplot=i+1, x=x['data'], xlabel=x['label'], xunit=x['unit'],
                                                   y=y['data'], ylabel=y['label'], yunit=y['unit'])
    def _get_2d_data(self,x,y,z):
        return reshape_2D_data(flatten_1D_data_for_plot(x['data']), 
                                                        flatten_1D_data_for_plot(y['data']), 
                                                        flatten_1D_data_for_plot(z['data']))
    def _add_2d(self, i, x, y, z):
        xrow, yrow, z_to_plot = self._get_2d_data(x,y,z)
        return self.add_to_plot(subplot=i+1, x=xrow, y=yrow, z=z_to_plot,
                                                    xlabel=x['label'], xunit=x['unit'],
                                                    ylabel=y['label'], yunit=y['unit'],
                                                    zlabel=z['label'], zunit=z['unit'])        
    
    
    def update_plots(self):
        
        alldata = get_data_by_id(self.id)

        # update all plots
        for trace, data in zip(self.traces, alldata):
            x = data[0]
            y = data[1]
            if len(data) == 2:  # 1D PLOTTING
                trace['plot_object'].setData(*self._line_data(x['data'], y['data']))

            elif len(data) == 3:  # 2D PLOTTING
                z = data[2]
                xrow, yrow, z_to_plot = self._get_2d_data(x,y,z)
                self._update_image(trace['plot_object'], {'x':xrow, 'y':yrow, 'z':z_to_plot})
        
    
#    def disconnect_subscriber(self):
#        dataset = load_by_id(self.id)
#        dataset.unsubscribe_all()
