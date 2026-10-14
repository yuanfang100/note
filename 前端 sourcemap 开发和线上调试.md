## 关于 sourcemap

#### 五个关键字

> sourcemap 多种配置项其实只是五个关键字 eval、source-map、cheap、module 和 inline 的组合

| 关键字     | 含义                                                         |
| :--------- | :----------------------------------------------------------- |
| source-map | 产生.map 文件，定位信息最完整，但 .map 文件最大，效率最低    |
| eval       | 使用 eval 包裹模块代码，利用字符串可缓存从而提效             |
| cheap      | 不包含列信息，也不包含 loader 的 sourcemap，用精准度降低换取文件内容的缩小，对于经由 babel 转换后的代码，只能定位到转换后的代码； |
| module     | 包含 loader 的 sourcemap（比如 jsx to js ，babel 的 sourcemap）,否则无法定义源文件,解决对于使用`cheap` 配置项导致无法定位到 loader 处理前的源代码问题 |
| inline     | 将.map 作为 DataURI 嵌入，不单独生成.map 文件，减少文件数    |

#### 各自的处理结果

##### 1、source-map 处理后输出结果

```go
//# sourceMappingURL=bundle.js.map
```

##### 2、eval 处理后输出结果

```js
eval("var a = 1,\n    b;\nb = a;\n\n//\n// WEBPACK FOOTER\n// ./src/index.js\n// module id = 0\n// module chunks = 0\n\n//# sourceURL=webpack:///./src/index.js?");
```

##### 3、`Inline-source-map`处理后输出结果

```js
//# sourceMappingURL=data: ...（base64 字符串）
```

##### 4、`cheap-source-map`处理后输出结果

```js
//# sourceMappingURL=bundle.js.map
```

##### 5、`cheap-module-source-map`处理后输出结果

```js
//# sourceMappingURL=bundle.js.map
```

#### 最佳实践

###### 开发环境

- 我们在开发环境对 sourceMap 的要求是：快（eval），信息全（module），
- 且由于此时代码未压缩，我们并不那么在意代码列信息(cheap),

所以开发环境比较推荐配置：`devtool: cheap-module-eval-source-map`

###### 生产环境

- 一般情况下，我们并不希望任何人都可以在浏览器直接看到我们未编译的源码，
- 所以我们不应该直接提供 sourceMap 给浏览器。但我们又需要 sourceMap 来定位我们的错误信息，
- 一方面 webpack 会生成 sourcemap 文件以提供给错误收集工具比如 sentry，另一方面又不会为 bundle 添加引用注释，以避免浏览器使用。

这时我们可以设置`devtool: hidden-source-map`



#### 最佳实践方式

线上环境： debug 

开发环境：sourcemap

速度最快： eval-cheap-source-map

调试友好：cheap-module-source-map

折中：eval-source-map





## 测试环境调试

1. devtool 设置成 false， 然后使用 webpack内置的 SourceMapDevToolPlugin 来精细化控制 sourcemap;

2.  生成的 .map 文件不能上传到线上环境，需要保留一份到本地以便 debug ；此时可以使用 filemanager-webpack-plugin 来完成先复制后删除的工作；

3. 用 http-server 来作为 maps 目录的静态服务器，向测试环境提供 map 文件服务；

   > 在 maps 目录中运行 `http-server -p 8081`

4. 浏览器开发者根据打开设置--->  sources ---> 启用 Enable javascript sourcemaps，到源码中打断点，开始 debug 旅程；

```js
const FileManager = require('filemanager-webpack-plugin')


devtool: false
plugins:[
    ... ,
    new webpack.SourceMapDevToolPlugin({
        // 向编译输出文件里添加 sourcemap 映射文本,得到结果, 192.168.1.104 是调试者的电脑ip 地址，\n//sourceMappingURL=http://192.168.1.104:8081/main.js.map 
        append:`\n//sourceMappingURL=http://192.168.1.104:8081/[url]`,
        filename: `[file].map` // 如 main.js.map
    })

    // 将 dist 下的 map 复制到 项目根目录下的 maps 目录，然后将 dist 下的吗 map 文件全部删除
    new FileManager({
        events:{
            onEnd:{
                copy:[
                    {
                        source: './dist/**/*.map', // 源路径
                        destination: path.resolve(__dirname,'maps') // 目标路径
                    }
                ],
                delete:['./dist/**/*.map']
            }
        }
    })
]
```



## 生产环境调试

> 同样将 map 文件放到本地，不上传到线上；

1. 此时映射文件的路径不添加到编译的输出文件中，因此不用 webpack.SourceMapDevToolPlugin 插件，仍然要使用 FileManager 进行复制删除的工作；

2. webpack 中配置 devtool，设置为 hidden-source-map，目的是生成 map 文件，但是不添加 map 映射路径到输出文件；

   ```js
   devtool: hidden-source-map
   ```

3. 部署打包后的代码，并访问；

4. 用 http-server 开启 maps 静态服务，找到要调试的 map 文件，到浏览器中访问，完整路径如 127.0.0.1:8080/main.js.map ， 将此路径完整复制下来；

5. 添加 map 映射路径。浏览器开发者工具--->控制台--->sources---> 选中要调试的代码-->在代码中右键--> Add source map... ---> 输入上一步复制好的路径；

6. 打断点，开启调试旅程；



## 生产环境下开启 vue-devtool 

#### 1、原理

`vue devtools扩展组件`会在window全局注入`__VUE_DEVTOOLS_GLOBAL_HOOK__`变量。只要你启用这个扩展组件，任意页面都可以看到这个属性。

vue根实例初始化之前判断`Vue.config.devtools`是否为true。若为true，则调用window.__VUE_DEVTOOLS_GLOBAL_HOOK__.emit('init', Vue)方法初始化调试面板，然后再打开 chrome 控制台就能看到 vue-devtool 面板了。

#### 2、操作

1. 打包到线上部署的代码，vue 源码一般会打包到 vendor.xxxx.js 文件中，在 chrome 的 sources 面板中找到此文件的代码，用面板左下角的 {} 使压缩后的代码格式化；

2. ctrl+f 搜索找到如下代码位置

   ```js
   X.devtools && ft && ft.emit("init", Wi)
   ```

   其中， `X`就是Vue.config, `ft`就是`window.__VUE_DEVTOOLS_GLOBAL_HOOK__`。因为这俩变量是代码混淆压缩后的命名，在不同的项目中可能是另外一种命名，寻找方式是相同的。

3. 在上一步的代码前面打个断点，然后刷新页面**(操作必须一致)**，此时页面会卡住，在console 控制台下输入如下代码并回车运行，以修改 devtools 配置，然后关闭 chrome 开发者，再打开，就能看到 vue-devtools 面板了。

   ```js
   X.devtools = 1 ; // 只要是 true 就可以
   ```

#### 注意

> 这个方法只是对当前标签页有效，就是说，如果不小心（出于习惯）刷新了一下页面，或者有新标签页打开其他路由的需求，就需要重新走一遍上面的步骤。





























