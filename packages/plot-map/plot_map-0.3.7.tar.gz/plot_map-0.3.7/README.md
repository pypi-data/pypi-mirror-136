# plot_map

## 安装

    pip install -U plot-map

## 底图加载功能

### 地图底图加载

只需要用以下代码：   

    import plot_map
    #设定显示范围
    bounds = [lon1,lat1,lon2,lat2]  
    plot_map.plot_map(plt,bounds,zoom = 12,style = 4)  

参数

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| bounds      | 底图的绘图边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 |
| zoom        | 底图的放大等级，越大越精细，加载的时间也就越久，一般单个城市大小的范围，这个参数选取12到16之间 |
| style       | 地图底图的样式，可选1-5，或'light','dark'，style为4时为light，style为5时为dark  |
| imgsavepath | 瓦片地图储存路径，设置路径后，会把地图下载到本地的文件夹下，使用时也会优先搜索是否有已经下载的瓦片，默认的存放路径是C:\\ |
| printlog    | 是否显示日志                                                 |

### 绘制指北针和比例尺的功能plotscale

为底图添加指北针和比例尺

    plot_map.plotscale(ax,bounds = bounds,textsize = 10,compasssize = 1,accuracy = 2000,rect = [0.06,0.03])  

参数

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| bounds      | 底图的绘图边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 |
| textsize    | 标注文字大小                                                 |
| compasssize | 标注的指北针大小                                             |
| accuracy    | 标注比例尺的长度                                             |
| unit        | 'KM','km','M','m' 比例尺的单位                               |
| style       | 1或2，比例尺样式                                             |
| rect       | 比例尺在图中的大致位置，如[0.9,0.9]则在右上角                    |
