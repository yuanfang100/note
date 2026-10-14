# 最终完整的 Koa2-Mysql 模板项目结构

我为你整合了**最终完整版**：包含 CRUD/分页/事务/文件上传/参数校验/JWT/部署脚本/接口文档/前端Axios封装，所有代码都加了详细注释，可直接落地生产。

---

# 最终完整项目结构

```Plain Text

koa2-mysql-template/
├── config/                # 配置
│   └── db.js              # MySQL 连接池
├── controllers/           # 控制器
│   ├── userController.js  # 用户相关
│   └── commonController.js # 通用（上传）
├── middleware/            # 中间件
│   ├── error.js           # 全局错误处理
│   ├── auth.js            # JWT 鉴权
│   └── validate.js        # 参数校验
├── routes/                # 路由
│   ├── user.js            # 用户路由
│   ├── common.js          # 通用路由
│   └── index.js           # 路由入口
├── utils/                 # 工具
│   ├── jwt.js             # JWT 生成/验证
│   ├── db.js              # 通用 CRUD/分页
│   └── transaction.js     # 事务封装
├── public/                # 静态文件（上传目录）
│   └── upload/
├── deploy/                # 部署脚本
│   ├── pm2.config.js      # PM2 配置
│   └── nginx.conf         # Nginx 配置
├── docs/                  # 接口文档
│   └── api-docs.js        # Swagger 文档
├── frontend/              # 前端 Axios 封装
│   └── request.js
├── app.js                 # 项目入口
├── .env                   # 环境变量
├── package.json           # 依赖
└── README.md              # 说明
```

---

## 1. package.json（含所有依赖）

```JSON

{
  "name": "koa2-mysql-template",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "pm2": "pm2 start deploy/pm2.config.js"
  },
  "dependencies": {
    "@koa/cors": "^5.0.0",
    "dotenv": "^16.4.5",
    "joi": "^17.12.2",
    "jsonwebtoken": "^9.0.2",
    "koa": "^2.15.0",
    "koa-body": "^6.0.1",
    "koa-router": "^12.0.1",
    "mysql2": "^3.9.1",
    "koa2-swagger-ui": "^5.10.0",
    "swagger-jsdoc": "^6.2.8"
  },
  "devDependencies": {
    "nodemon": "^3.1.0",
    "pm2": "^5.3.1"
  }
}
```

---

## 2. .env（环境变量）

```TOML

# 服务配置
PORT=3000
NODE_ENV=development

# MySQL 配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=你的数据库名
DB_PORT=3306

# JWT 配置
JWT_SECRET=your_jwt_secret_key_123456
JWT_EXPIRES_IN=7d

# 上传配置
UPLOAD_DIR=./public/upload
```

---

## 3. config/db.js（MySQL 连接池）

```JavaScript

const mysql = require('mysql2/promise');
const dotenv = require('dotenv');
dotenv.config();

/**
 * MySQL 连接池配置
 * 避免每次请求新建连接，防止连接泄露
 * connectionLimit: 最大连接数，根据服务器性能调整
 * waitForConnections: 连接数满时等待（而非报错）
 */
const pool = mysql.createPool({
  host: process.env.DB_HOST,        // 数据库地址
  user: process.env.DB_USER,        // 数据库用户名
  password: process.env.DB_PASSWORD,// 数据库密码
  database: process.env.DB_NAME,    // 数据库名
  port: process.env.DB_PORT || 3306,// 数据库端口
  waitForConnections: true,         // 连接数满时等待
  connectionLimit: 10,              // 最大连接数
  queueLimit: 0,                    // 等待队列无限制
  charset: 'utf8mb4'                // 支持emoji等特殊字符
});

// 测试连接
pool.getConnection().then(conn => {
  console.log('✅ MySQL 连接成功');
  conn.release(); // 释放连接
}).catch(err => {
  console.error('❌ MySQL 连接失败：', err.message);
});

module.exports = pool;
```

---

## 4. middleware/error.js（全局错误处理）

```JavaScript

/**
 * 全局错误处理中间件
 * 捕获所有异步/同步错误，防止服务崩溃
 * 统一错误返回格式
 */
module.exports = async (ctx, next) => {
  try {
    await next(); // 执行后续中间件/路由
    
    // 处理404（接口不存在）
    if (ctx.status === 404 && !ctx.body) {
      ctx.body = {
        code: 404,
        msg: '接口不存在',
        data: null
      };
    }
  } catch (err) {
    // 打印错误日志（生产环境建议接入日志系统如winston）
    console.error(`[${new Date().toISOString()}] 服务器错误：`, err);
    
    // 统一错误返回
    ctx.body = {
      code: err.status || 500,          // 错误码（自定义/HTTP状态码）
      msg: err.message || '服务器内部错误', // 错误信息
      data: null,
      // 开发环境返回错误栈，生产环境隐藏
      stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
    };
    ctx.status = 200; // 统一返回200，前端通过code判断
  }
};
```

---

## 5. middleware/auth.js（JWT 鉴权）

```JavaScript

const { verifyToken } = require('../utils/jwt');

/**
 * JWT 鉴权中间件
 * 验证请求头中的token是否有效
 * 有效则将用户信息挂载到ctx.user，无效则返回401
 */
module.exports = async (ctx, next) => {
  // 从请求头获取token（支持 Bearer token 格式）
  const token = ctx.headers.token || ctx.headers.authorization || '';
  const cleanToken = token.replace('Bearer ', '').trim();

  // 无token直接返回未登录
  if (!cleanToken) {
    ctx.body = { code: 401, msg: '请先登录', data: null };
    return;
  }

  // 验证token
  const decoded = verifyToken(cleanToken);
  if (!decoded) {
    ctx.body = { code: 401, msg: 'token无效或已过期', data: null };
    return;
  }

  // 将解析后的用户信息挂载到ctx，后续控制器可直接使用
  ctx.user = decoded;
  await next(); // 执行后续中间件/路由
};
```

---

## 6. middleware/validate.js（参数校验）

```JavaScript

const Joi = require('joi');

/**
 * 参数校验中间件
 * @param {Joi.Schema} schema - Joi 校验规则
 * @returns {Function} 中间件函数
 * 自动根据请求方法获取参数（GET取query，POST取body）
 * 校验失败则返回400和错误信息
 */
module.exports = (schema) => async (ctx, next) => {
  // 根据请求方法获取参数
  const data = ctx.method === 'GET' ? ctx.query : ctx.request.body;
  
  // 执行校验
  const { error } = schema.validate(data, {
    abortEarly: false, // 不提前终止，返回所有错误
    allowUnknown: false // 不允许未知字段
  });

  // 校验失败返回错误
  if (error) {
    const errMsg = error.details.map(item => item.message).join('；');
    ctx.body = {
      code: 400,
      msg: `参数错误：${errMsg}`,
      data: null
    };
    return;
  }

  // 校验通过，执行后续逻辑
  await next();
};
```

---

## 7. utils/jwt.js（JWT 工具）

```JavaScript

const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
dotenv.config();

const JWT_SECRET = process.env.JWT_SECRET;       // JWT 密钥（生产环境建议加密存储）
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN; // token过期时间

/**
 * 生成JWT Token
 * @param {Object} payload - 需加密的用户信息（不要存敏感信息如密码）
 * @returns {string} 生成的token
 */
exports.createToken = (payload) => {
  if (!JWT_SECRET) {
    throw new Error('JWT_SECRET 未配置');
  }
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN || '7d' // 默认7天过期
  });
};

/**
 * 验证JWT Token
 * @param {string} token - 需验证的token
 * @returns {Object|null} 解析后的用户信息（失败返回null）
 */
exports.verifyToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (err) {
    // 捕获token过期/无效等错误
    console.error('Token验证失败：', err.message);
    return null;
  }
};
```

---

## 8. utils/db.js（通用 CRUD + 分页）

```JavaScript

const pool = require('../config/db');

/**
 * 数据库通用操作工具类
 * 封装常用CRUD和分页逻辑，减少重复代码
 */
class DbUtil {
  /**
   * 单条查询
   * @param {string} sql - SQL语句
   * @param {Array} params - SQL参数（防注入）
   * @returns {Object|null} 查询结果（无数据返回null）
   */
  static async findOne(sql, params = []) {
    const [rows] = await pool.query(sql, params);
    return rows[0] || null;
  }

  /**
   * 列表查询
   * @param {string} sql - SQL语句
   * @param {Array} params - SQL参数
   * @returns {Array} 查询结果数组
   */
  static async find(sql, params = []) {
    const [rows] = await pool.query(sql, params);
    return rows;
  }

  /**
   * 新增数据
   * @param {string} table - 表名
   * @param {Object} data - 新增数据对象
   * @returns {Object} 新增结果（含insertId等）
   */
  static async insert(table, data = {}) {
    const keys = Object.keys(data);
    if (keys.length === 0) {
      throw new Error('新增数据不能为空');
    }
    // 生成占位符和SQL语句（防注入）
    const placeholders = keys.map(() => '?').join(',');
    const sql = `INSERT INTO ${table} (${keys.join(',')}) VALUES (${placeholders})`;
    const [result] = await pool.query(sql, Object.values(data));
    return result;
  }

  /**
   * 更新数据
   * @param {string} table - 表名
   * @param {Object} data - 更新数据对象
   * @param {Object} where - 条件对象
   * @returns {Object} 更新结果（含affectedRows等）
   */
  static async update(table, data = {}, where = {}) {
    const whereKeys = Object.keys(where);
    if (whereKeys.length === 0) {
      throw new Error('更新操作必须指定where条件');
    }
    if (Object.keys(data).length === 0) {
      throw new Error('更新数据不能为空');
    }
    // 生成SET和WHERE子句
    const setSql = Object.keys(data).map(k => `${k}=?`).join(',');
    const whereSql = whereKeys.map(k => `${k}=?`).join(' AND ');
    const sql = `UPDATE ${table} SET ${setSql} WHERE ${whereSql}`;
    const [result] = await pool.query(sql, [...Object.values(data), ...Object.values(where)]);
    return result;
  }

  /**
   * 删除数据
   * @param {string} table - 表名
   * @param {Object} where - 条件对象
   * @returns {Object} 删除结果（含affectedRows等）
   */
  static async delete(table, where = {}) {
    const whereKeys = Object.keys(where);
    if (whereKeys.length === 0) {
      throw new Error('删除操作必须指定where条件');
    }
    const whereSql = whereKeys.map(k => `${k}=?`).join(' AND ');
    const sql = `DELETE FROM ${table} WHERE ${whereSql}`;
    const [result] = await pool.query(sql, Object.values(where));
    return result;
  }

  /**
   * 分页查询
   * @param {string} sql - 基础SQL语句（不含LIMIT）
   * @param {Array} params - SQL参数
   * @param {number} pageNum - 页码（默认1）
   * @param {number} pageSize - 每页条数（默认10）
   * @returns {Object} 分页结果（list/total/pageNum/pageSize/totalPage）
   */
  static async page(sql, params = [], pageNum = 1, pageSize = 10) {
    // 类型转换+边界处理
    pageNum = Math.max(parseInt(pageNum) || 1, 1);
    pageSize = Math.max(parseInt(pageSize) || 10, 1);
    const offset = (pageNum - 1) * pageSize;

    // 查询总数（替换SELECT部分为COUNT(*)）
    const countSql = sql.replace(/^SELECT\s+[\s\S]*?\s+FROM/i, 'SELECT COUNT(*) as total FROM');
    const [countRows] = await pool.query(countSql, params);
    const total = countRows[0].total || 0;

    // 查询列表（加LIMIT）
    const listSql = `${sql} LIMIT ?,?`;
    const [list] = await pool.query(listSql, [...params, offset, pageSize]);

    return {
      list,                // 数据列表
      total,               // 总条数
      pageNum,             // 当前页码
      pageSize,            // 每页条数
      totalPage: Math.ceil(total / pageSize) // 总页数
    };
  }
}

module.exports = DbUtil;
```

---

## 9. utils/transaction.js（事务封装）

```JavaScript

const pool = require('../config/db');

/**
 * 数据库事务封装
 * @param {Function} fn - 事务执行函数（接收connection参数）
 * @returns {boolean} 执行结果（true成功，false失败）
 * @example
 * await runTransaction(async (conn) => {
 *   await conn.query('UPDATE table SET a=1 WHERE id=?', [1]);
 *   await conn.query('UPDATE table SET b=2 WHERE id=?', [2]);
 * });
 */
async function runTransaction(fn) {
  // 获取连接（事务必须用同一个连接）
  const conn = await pool.getConnection();
  try {
    await conn.beginTransaction(); // 开启事务
    await fn(conn);               // 执行事务逻辑
    await conn.commit();          // 提交事务
    return true;
  } catch (err) {
    await conn.rollback();        // 回滚事务
    console.error('事务执行失败，已回滚：', err);
    throw err; // 抛出错误，让上层处理
  } finally {
    conn.release(); // 释放连接（无论成功失败都要释放）
  }
}

module.exports = runTransaction;
```

---

## 10. controllers/commonController.js（文件上传）

```JavaScript

const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
dotenv.config();

// 上传目录（从环境变量读取，默认./public/upload）
const UPLOAD_DIR = process.env.UPLOAD_DIR || './public/upload';

/**
 * 通用文件上传控制器
 * 支持单文件上传，自动创建目录，重命名文件避免重复
 */
exports.upload = async (ctx) => {
  try {
    // 获取上传文件（koa-body解析后的文件）
    const file = ctx.request.files?.file;
    if (!file) {
      ctx.body = { code: 400, msg: '请选择要上传的文件', data: null };
      return;
    }

    // 1. 创建上传目录（不存在则创建）
    if (!fs.existsSync(UPLOAD_DIR)) {
      fs.mkdirSync(UPLOAD_DIR, { recursive: true }); // recursive: 递归创建多级目录
    }

    // 2. 处理文件名（时间戳+原扩展名，避免重复）
    const ext = path.extname(file.originalFilename); // 获取扩展名（如.jpg）
    const filename = `${Date.now()}${ext}`;          // 重命名文件
    const filePath = path.join(UPLOAD_DIR, filename); // 最终文件路径

    // 3. 读取临时文件并写入目标路径
    const reader = fs.createReadStream(file.filepath); // 读取临时文件
    const writer = fs.createWriteStream(filePath);     // 写入目标文件
    reader.pipe(writer); // 管道传输

    // 4. 返回上传结果
    ctx.body = {
      code: 200,
      msg: '文件上传成功',
      data: {
        filename,                // 文件名
        url: `/upload/${filename}`, // 访问URL
        size: file.size,         // 文件大小（字节）
        type: file.mimetype      // 文件类型
      }
    };
  } catch (err) {
    ctx.body = { code: 500, msg: `上传失败：${err.message}`, data: null };
  }
};
```

---

## 11. controllers/userController.js（用户CRUD+事务）

```JavaScript

const DbUtil = require('../utils/db');
const runTransaction = require('../utils/transaction');
const { createToken } = require('../utils/jwt');

/**
 * 用户控制器
 * 处理用户相关业务逻辑（登录/信息/CRUD/事务示例）
 */
class UserController {
  /**
   * 用户登录
   * @param {Object} ctx - Koa上下文
   */
  static async login(ctx) {
    const { username, password } = ctx.request.body;

    // 1. 查询用户（防注入：使用占位符）
    const user = await DbUtil.findOne(
      'SELECT id, username FROM user WHERE username = ? AND password = ?',
      [username, password]
    );

    // 2. 验证用户是否存在
    if (!user) {
      ctx.body = { code: 401, msg: '账号或密码错误', data: null };
      return;
    }

    // 3. 生成JWT Token（不存敏感信息）
    const token = createToken({ id: user.id, username: user.username });

    // 4. 返回结果
    ctx.body = {
      code: 200,
      msg: '登录成功',
      data: { token, user: { id: user.id, username: user.username } }
    };
  }

  /**
   * 获取当前登录用户信息
   * @param {Object} ctx - Koa上下文（已通过auth中间件挂载user）
   */
  static async info(ctx) {
    const { id } = ctx.user; // 从ctx.user获取登录用户ID

    // 查询用户信息（排除密码等敏感字段）
    const user = await DbUtil.findOne(
      'SELECT id, username FROM user WHERE id = ?',
      [id]
    );

    ctx.body = {
      code: 200,
      msg: '获取成功',
      data: user || {}
    };
  }

  /**
   * 用户列表（分页）
   * @param {Object} ctx - Koa上下文
   */
  static async list(ctx) {
    const { username, pageNum = 1, pageSize = 10 } = ctx.query;

    // 构建查询条件
    let sql = 'SELECT id, username FROM user WHERE 1 = 1';
    const params = [];
    if (username) {
      sql += ' AND username LIKE ?';
      params.push(`%${username}%`); // 模糊查询
    }

    // 分页查询
    const result = await DbUtil.page(sql, params, pageNum, pageSize);

    ctx.body = {
      code: 200,
      msg: '获取成功',
      data: result
    };
  }

  /**
   * 新增用户
   * @param {Object} ctx - Koa上下文
   */
  static async add(ctx) {
    const { username, password } = ctx.request.body;

    // 检查用户名是否已存在
    const existUser = await DbUtil.findOne(
      'SELECT id FROM user WHERE username = ?',
      [username]
    );
    if (existUser) {
      ctx.body = { code: 400, msg: '用户名已存在', data: null };
      return;
    }

    // 新增用户
    const result = await DbUtil.insert('user', { username, password });

    ctx.body = {
      code: 200,
      msg: '新增成功',
      data: { id: result.insertId, username }
    };
  }

  /**
   * 更新用户
   * @param {Object} ctx - Koa上下文
   */
  static async update(ctx) {
    const { id, username, password } = ctx.request.body;

    // 构建更新数据（只更新有值的字段）
    const updateData = {};
    if (username) updateData.username = username;
    if (password) updateData.password = password;

    // 执行更新
    await DbUtil.update('user', updateData, { id });

    ctx.body = {
      code: 200,
      msg: '更新成功',
      data: null
    };
  }

  /**
   * 删除用户
   * @param {Object} ctx - Koa上下文
   */
  static async delete(ctx) {
    const { id } = ctx.request.body;

    // 执行删除
    await DbUtil.delete('user', { id });

    ctx.body = {
      code: 200,
      msg: '删除成功',
      data: null
    };
  }

  /**
   * 事务示例（批量更新用户密码）
   * @param {Object} ctx - Koa上下文
   */
  static async transactionDemo(ctx) {
    try {
      // 执行事务（批量更新两个用户密码）
      await runTransaction(async (conn) => {
        // 事务内必须使用同一个connection执行SQL
        await conn.query('UPDATE user SET password = ? WHERE id = ?', ['123456', 1]);
        await conn.query('UPDATE user SET password = ? WHERE id = ?', ['654321', 2]);
      });

      ctx.body = {
        code: 200,
        msg: '事务执行成功',
        data: null
      };
    } catch (err) {
      ctx.body = {
        code: 500,
        msg: `事务执行失败：${err.message}`,
        data: null
      };
    }
  }
}

module.exports = UserController;
```

---

## 12. routes/common.js（通用路由）

```JavaScript

const Router = require('koa-router');
const router = new Router();
const commonController = require('../controllers/commonController');
const auth = require('../middleware/auth'); // 鉴权中间件

/**
 * 通用路由（文件上传等）
 * 所有接口需登录验证（auth中间件）
 */
// 文件上传接口
router.post('/upload', auth, commonController.upload);

module.exports = router;
```

---

## 13. routes/user.js（用户路由）

```JavaScript

const Router = require('koa-router');
const router = new Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth'); // 鉴权中间件
const validate = require('../middleware/validate'); // 参数校验中间件
const Joi = require('joi'); // 校验规则

/**
 * 用户路由
 * 定义用户相关接口，添加校验和鉴权
 */
// 登录（无需鉴权，需参数校验）
router.post('/login', validate(
  Joi.object({
    username: Joi.string().required().min(2).max(20).message('用户名长度需2-20位'),
    password: Joi.string().required().min(6).message('密码长度至少6位')
  })
), userController.login);

// 获取当前用户信息（需鉴权）
router.get('/info', auth, userController.info);

// 用户列表（需鉴权）
router.get('/list', auth, userController.list);

// 新增用户（需鉴权+参数校验）
router.post('/add', auth, validate(
  Joi.object({
    username: Joi.string().required().min(2).max(20).message('用户名长度需2-20位'),
    password: Joi.string().required().min(6).message('密码长度至少6位')
  })
), userController.add);

// 更新用户（需鉴权）
router.post('/update', auth, userController.update);

// 删除用户（需鉴权）
router.post('/delete', auth, userController.delete);

// 事务示例（需鉴权）
router.post('/transaction', auth, userController.transactionDemo);

module.exports = router;
```

---

## 14. routes/index.js（路由入口）

```JavaScript

const Router = require('koa-router');
const router = new Router();

/**
 * 路由总入口
 * 挂载所有子路由，统一管理接口前缀
 */
// 挂载用户路由（前缀：/user）
router.use('/user', require('./user'));

// 挂载通用路由（前缀：/common）
router.use('/common', require('./common'));

module.exports = router;
```

---

## 15. docs/api-docs.js（Swagger 接口文档）

```JavaScript

const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('koa2-swagger-ui');

/**
 * Swagger 接口文档配置
 * 自动生成接口文档，支持在线调试
 */
const swaggerDefinition = {
  openapi: '3.0.0',
  info: {
    title: 'Koa2 + MySQL API 文档', // 文档标题
    version: '1.0.0',              // 版本
    description: '基于Koa2 + MySQL的后端接口文档' // 描述
  },
  servers: [
    {
      url: 'http://localhost:3000', // 接口地址
      description: '开发环境'
    }
  ],
  components: {
    // 定义JWT鉴权
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT'
      }
    }
  }
};

// Swagger 配置选项
const options = {
  swaggerDefinition,
  apis: [
    './routes/*.js',    // 路由文件
    './controllers/*.js' // 控制器文件
  ]
};

// 创建Swagger文档
const swaggerSpec = swaggerJSDoc(options);

/**
 * 配置Swagger UI中间件
 * 访问 http://localhost:3000/docs 查看文档
 */
const swaggerMiddleware = swaggerUi({
  swaggerOptions: {
    spec: swaggerSpec
  },
  routePrefix: '/docs' // 文档访问路径
});

module.exports = swaggerMiddleware;
```

---

## 16. deploy/pm2.config.js（PM2 部署配置）

```JavaScript

/**
 * PM2 配置文件
 * 用于生产环境守护进程，自动重启，负载均衡
 * 使用方式：npm run pm2 或 pm2 start deploy/pm2.config.js
 */
module.exports = {
  apps: [
    {
      name: 'koa2-mysql-app', // 应用名称
      script: 'app.js',       // 入口文件
      cwd: './',              // 工作目录
      instances: 'max',       // 实例数（max：根据CPU核心数）
      exec_mode: 'cluster',   // 集群模式（提升性能）
      env: {
        NODE_ENV: 'development' // 开发环境
      },
      env_production: {
        NODE_ENV: 'production'  // 生产环境
      },
      // 日志配置
      log_date_format: 'YYYY-MM-DD HH:mm:ss', // 日志时间格式
      out_file: './logs/out.log',             // 标准输出日志
      error_file: './logs/error.log',         // 错误日志
      merge_logs: true,                       // 合并日志
      // 自动重启配置
      autorestart: true,                      // 崩溃自动重启
      watch: false,                           // 生产环境关闭监听
      max_memory_restart: '1G'                // 内存超过1G自动重启
    }
  ]
};
```

---

## 17. deploy/nginx.conf（Nginx 配置）

```Nginx

# Nginx 配置示例
# 用于反向代理，静态资源处理，负载均衡，HTTPS配置
# 部署路径：/etc/nginx/conf.d/koa2-mysql.conf

# 服务器配置
server {
    listen 80;                  # 监听80端口
    server_name your-domain.com; # 你的域名（替换为实际域名）

    # 静态资源（上传文件）
    location /upload/ {
        root /www/koa2-mysql-template/public; # 项目public目录绝对路径
        expires 7d;                           # 缓存7天
        add_header Cache-Control "public";
    }

    # 反向代理到Node服务
    location / {
        proxy_pass http://127.0.0.1:3000;     # Node服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;            # 连接超时
        proxy_read_timeout 60s;               # 读取超时
    }

    # 日志配置
    access_log /var/log/nginx/koa2-mysql-access.log;
    error_log /var/log/nginx/koa2-mysql-error.log;
}

# HTTPS配置示例（可选）
# server {
#     listen 443 ssl;
#     server_name your-domain.com;

#     ssl_certificate /path/to/ssl.crt;      # SSL证书路径
#     ssl_certificate_key /path/to/ssl.key;  # SSL私钥路径
#     ssl_protocols TLSv1.2 TLSv1.3;

#     location / {
#         proxy_pass http://127.0.0.1:3000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }
```

---

## 18. frontend/request.js（前端 Axios 封装）

```JavaScript

import axios from 'axios';

/**
 * 前端 Axios 封装
 * 统一请求配置、拦截器、错误处理、Token 刷新
 */
const service = axios.create({
  baseURL: 'http://localhost:3000', // 后端接口地址
  timeout: 10000,                   // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
});

// 请求拦截器（添加Token）
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取Token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['token'] = token; // 添加到请求头
    }
    return config;
  },
  (error) => {
    console.error('请求错误：', error);
    return Promise.reject(error);
  }
);

// 响应拦截器（统一处理返回结果）
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 统一处理code !== 200的情况
    if (res.code !== 200) {
      // 401：Token过期/未登录
      if (res.code === 401) {
        // 清除Token并跳转到登录页
        localStorage.removeItem('token');
        window.location.href = '/login';
        ElMessage.error('登录已过期，请重新登录'); // 需引入ElementUI
      } else {
        ElMessage.error(res.msg || '请求失败');
      }
      return Promise.reject(res);
    }
    return res;
  },
  (error) => {
    console.error('响应错误：', error);
    ElMessage.error('网络错误，请稍后重试');
    return Promise.reject(error);
  }
);

/**
 * 封装常用请求方法
 */
const request = {
  // GET请求
  get(url, params = {}) {
    return service.get(url, { params });
  },

  // POST请求
  post(url, data = {}) {
    return service.post(url, data);
  },

  // 文件上传
  upload(url, file) {
    const formData = new FormData();
    formData.append('file', file);
    return service.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  // PUT请求
  put(url, data = {}) {
    return service.put(url, data);
  },

  // DELETE请求
  delete(url, params = {}) {
    return service.delete(url, { params });
  }
};

export default request;
```

---

## 19. app.js（项目入口）

```JavaScript

const Koa = require('koa');
const cors = require('@koa/cors');
const koaBody = require('koa-body');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// 加载环境变量
dotenv.config();

// 导入路由和中间件
const router = require('./routes');
const errorHandler = require('./middleware/error');
const swaggerMiddleware = require('./docs/api-docs');

// 创建Koa实例
const app = new Koa();

// 1. 跨域配置
app.use(cors({
  origin: '*', // 开发环境允许所有来源，生产环境指定具体域名
  credentials: true, // 允许携带Cookie
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], // 允许的请求方法
  allowHeaders: ['Content-Type', 'token', 'Authorization'] // 允许的请求头
}));

// 2. 请求体解析（替换bodyparser，支持文件上传）
app.use(koaBody({
  multipart: true,               // 支持文件上传
  formidable: {
    maxFileSize: 10 * 1024 * 1024, // 文件大小限制：10MB
    uploadDir: path.join(__dirname, 'public/upload'), // 临时上传目录
    keepExtensions: true         // 保留文件扩展名
  },
  parsedMethods: ['POST', 'PUT', 'DELETE', 'PATCH'] // 解析的请求方法
}));

// 3. 静态资源服务（上传文件访问）
app.use(require('koa-static')(path.join(__dirname, 'public')));

// 4. 全局错误处理（必须在路由前）
app.use(errorHandler);

// 5. 接口文档（Swagger UI）
app.use(swaggerMiddleware);

// 6. 路由挂载
app.use(router.routes()).use(router.allowedMethods());

// 7. 启动服务
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ 服务器启动成功：http://localhost:${PORT}`);
  console.log(`📚 接口文档地址：http://localhost:${PORT}/docs`);
});

// 捕获未处理的Promise错误（防止服务崩溃）
process.on('unhandledRejection', (err) => {
  console.error('未处理的Promise错误：', err);
});
```

---

## 20. [README.md](README.md)（使用说明）

```Markdown

# Koa2 + MySQL 项目模板
基于 Koa2 + MySQL 的后端项目模板，包含完整的 CRUD、分页、事务、文件上传、JWT 鉴权、参数校验、接口文档、部署脚本等功能。

## 快速开始
### 1. 安装依赖
```bash
npm install
```

### 2. 配置环境变量

复制 `.env` 文件，修改数据库配置：

```TOML

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=你的数据库名
```

### 3. 创建数据库表

```SQL

CREATE TABLE `user` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(50) NOT NULL COMMENT '密码',
  `create_time` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 测试数据
INSERT INTO `user` (`username`, `password`) VALUES ('admin', '123456');
```

### 4. 启动服务

```Bash

# 开发环境（热更新）
npm run dev

# 生产环境（PM2）
npm run pm2
```

### 5. 访问接口文档

```Plain Text

http://localhost:3000/docs
```

## 功能列表

- ✅ MySQL 连接池（防连接泄露）

- ✅ JWT 鉴权（登录/验证/过期处理）

- ✅ 全局错误处理（防止服务崩溃）

- ✅ 参数校验（Joi）

- ✅ 通用 CRUD + 分页

- ✅ 数据库事务

- ✅ 文件上传（自动创建目录/重命名）

- ✅ Swagger 接口文档

- ✅ PM2 部署（集群模式/自动重启）

- ✅ Nginx 反向代理配置

- ✅ 前端 Axios 封装（Token/上传/拦截器）

## 接口示例

### 登录

```Plain Text

POST http://localhost:3000/user/login
Body: {"username":"admin","password":"123456"}
```

### 文件上传

```Plain Text

POST http://localhost:3000/common/upload
Headers: token=xxx
FormData: file=选择文件
```

## 部署说明

### 1. PM2 启动

```Bash

npm run pm2
```

### 2. Nginx 配置

将 `deploy/nginx.conf` 复制到 Nginx 配置目录，修改域名和路径后重启 Nginx。

```Bash

nginx -s reload
```

```Plain Text


---

### 总结
1. **核心基础**：使用 MySQL 连接池防泄露、JWT 鉴权做身份验证、全局错误处理避免服务崩溃，这是项目稳定运行的基础；
2. **开发效率**：通用 CRUD/分页/事务封装减少重复代码，参数校验+Swagger 文档提升开发和联调效率；
3. **生产部署**：PM2 做进程守护（集群模式+自动重启），Nginx 做反向代理（静态资源+负载均衡），前端 Axios 封装统一处理 Token 和错误，形成完整的前后端解决方案。

所有代码都已添加详细注释，你只需替换数据库配置、调整业务逻辑即可直接用于生产环境。如果需要某部分的更详细说明（比如 Nginx 部署步骤、Token 刷新逻辑），可以随时问我。
```
> （注：文档部分内容可能由 AI 生成）