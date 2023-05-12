# 使用方法

ha 配置所在目录下新建如下目录结构

custom_components/weathernmc

把本项目文件放到
weathernmc 下

在 configuration.yaml 增加配置

    weather:
    - platform: weathernmc
        code: 53698

web 页面直接添加天气预报卡片就ok


code 查询
[查询气象站code](https://www.1an.com/h5/product/convention/9901_b.html)