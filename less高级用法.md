each 循环用法

1. 单层循环
   ```less
   @bgs: f00, fff, ededed;
   // .bg(@bg) {
   //   background-color: ~'#@{bg}'; // 将普通字符和变量拼接
   // }
   each(@bgs, {
     .bg-@{value} {
       background-color: ~ '#@{value}' ; // 将普通字符和变量拼接
     }
   });
   ```
2. 多层嵌套循环
   ```less
   @positions: bottom, top;
   @colors: 000, 333, 555, 666, 999, ccc, E5E5E5;

   each(@positions, .(@pVal, @pKey, @pIdx) {
     each(@colors, .(@cVal, @cKey, @cIdx) {
       .border-@{pVal}-@{cVal} {
         border-@{pVal}: ~'1px solid #@{cVal}';
       } 
     })
   })  
   ```

when 循环用法

```less
.cont(@count) when (@count > 0) {
  .cont((@count - 1));
  width: (25px * @count);
}
div {
  .cont(7);
}
```

生成

```css
div {
  width: 25px;
  width: 50px;
  width: 75px;
  width: 100px;
  width: 125px;
  width: 150px;
  width: 175px;
}
```

Less没有if / else 但是less具有一个when，and，not与“，”语法。

1. when 表示 在使用Mixin的时候必须满足 when后面的条件

```less
#box(@width, @height, @color) when (@width > 100px){
    width: @width;
    height: @height;
    background-color: @color;
}

.box{
    #box(101px,50px,pink)
}
```

2. 如果有两个必须同时满足的条件,使用 and

   ```less
   // 这里必须满足传递的宽度和颜色必须同时同满足条件才能执行Mixin
   #box(@width, @height, @color) when (@width > 100px) and (@color = pink){
       width: @width;
       height: @height;
       background-color: @color;
   }

   .box{
       #box(100px,50px,skyblue)
   }
   ```
3. 如果需要排除某个条件才能使用Mixin,使用not

   ```less
   // 这里排除颜色为pink ,除了pink颜色值都可以运行Mixin
   #box(@width, @height, @color) when  not (@color = pink){
       width: @width;
       height: @height;
       background-color: @color;
   }

   .box{
       #box(100px,50px,skyblue)
   }
   ```
4. 如果需要多个条件只要满足一个就执行Mixin,使用 逗号,

```less
// 虽然不满足宽度大于等于100px,但是满足为了颜色是skyblue 所以Mixin会执行
#box(@width, @height, @color) when (@width >= 100px),(@color = skyblue){
    width: @width;
    height: @height;
    background-color: @color;
}

.box{
    #box(50px,50px,skyblue)
}
```

object-fit  的四个值

内容拉伸(fill)，内容全部都显示(contain)，容器没有留白(cover)，该多大就多大(none)。

LHS和RHS的理解

打屁屁的小痘痘

- LHS：赋值操作的目标
  RHS：赋值操作的源头
- LHS：当变量出现在赋值操作的左侧时进行LHS查询
  LHS查询试图找到变量容器本 身
  如果查找的目的是对变量进行赋值，就会使用LHS
- RHS：当变量出现在赋值操作的右侧时进行RHS查询
  RHS查询就是简单的查找某个 变量的值
  如果目的是获取变量，就会使用RHS

```javascript
console.log(a)//其中对a的引用是一个RHS引用，因为其中的a并没被赋值，这里需要查找并取得a的值
```

LHS和RHS的含义是“赋值操作的左侧和右侧”，并不一定意味着“=”赋值操作符的左侧或者右侧。

```javascript
function foo(a){
    console.log(a);
};
foo(2);
```

调用函数foo(...)时对函数进行RHS引用
代码中隐式的a=2，是LHS查询，给参数a分配值
对console对象进行RHS查询，检查得到的值总是否有一个叫做log的方法
console.log(.....)中对a进行RHS引用

不成功的RHS引用会导致程序抛出ReferenceError异常
不成功的LHS应用会导致自动隐式地创建一个全局变量(非严格模式下)，该变量使用LHS引用的目标作为标识符，或者抛出ReferenceError异常(严格模式下)


## 输入框限制只能输入5位数字

```html
<input type="number" maxlength="5" /> <!--无法满足最多只能输入五位正整数的要求-->
```

* 当 **type="text"** ，上面代码可以限制五位
* 当 **type="number"** ，上面代码没法限制五位，可以无限输入位数
* 使用正则还有一个原因是：**type="number" **时可以输入 **e **字母和 **- **字符

```html
<input type="text" oninput="value=value.replace(/^(0+)|[^\d]+/g, '').slice(0, 5)" />`
```

- 输入的时候将不满足条件的字符用空字符串替换。
- 正则解读：/^(0+)|[^\d]+/g。
- ^(0+) 的意思是匹配一个或多个0开头的字符。
- [^\d] 一个反向字符集。也就是说， 它匹配任何没有包含在方括号中的字符。
- \d 匹配一个数字。等价于 [0-9]。
- [^\d] 的意思就是匹配所有不是数字 0-9 的字符
- 总的意思就是输入的开头为0或多个0的会被去除，输入的内容中（不一定是开头），如果有不是 0-9 的数字的字符也会被去除
- slice(0, 5) 就是限制5位数
  所以这样就保证了输入的内容一定是正整数

```js
// 比如只能输入0--100
function formatValue(value, max){
    if(value[0] == 0) return 0;
    var maxLen = (''+max).length;
    // 把不是数字的和前面的多个0 全清除掉
    value = value.replace(/^(0+)|[^\d]+/g, '').slice(0, maxLen);
    if(+value > max){
       value = value.slice(0,maxLen-1)
    }
    return value
}
```
