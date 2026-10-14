<template>
  <div class="container" ref="container">
    <Form v-if="more" class="layout-form">
      <FormItem label="设备序列号：">
        <i-input
          v-model.trim="query.fDeviceSN"
          placeholder="请输入设备序列号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem label="测试类型：">
        <i-select
          clearable
          v-model.trim="query.fTestType"
          placeholder="请选择测试类型"
          @keyup.enter.native="checkPermission('1096:select', search)"
        >
          <i-option v-for="(item,key) in testType" :key="key" :value="key">{{ item }}</i-option>
        </i-select>
      </FormItem>
      <FormItem label="工单号：">
        <i-input
          v-model.trim="query.fProductionBatchNumber"
          placeholder="请输入FC300R工单号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem label="笔记本序列号：">
        <i-input
          v-model.trim="query.fLaptopSerialNo"
          placeholder="请输入笔记本序列号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem label="指纹仪序列号：">
        <i-input
          v-model.trim="query.fFingerprintSerialNo"
          placeholder="请输入指纹仪序列号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem label="补光灯序列号：">
        <i-input
          v-model.trim="query.fFillLightSerialNo"
          placeholder="请输入补光灯序列号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem label="虹膜序列号：">
        <i-input
          v-model.trim="query.fIrisSn"
          placeholder="请输入虹膜序列号"
          @keyup.enter.native="checkPermission('1096:select', search)"
        />
      </FormItem>
      <FormItem class="operate">
        <Button type="primary" @click="checkPermission('1096:select', search)"
        >查询
        </Button
        >
        <Button @click="checkPermission('1096:select', reset)">重置</Button>
        <Button @click="more = false">隐藏</Button>
      </FormItem>
    </Form>
    <div class="layout-operate">
      <div class="btn-group">
<!--        <Button type="primary" @click="checkPermission('1096:save', add)">新增</Button>-->
        <Button @click="checkPermission('1096:delete', batchDel)">删除</Button>
        <Button @click="checkPermission('1096:export', exportExcel)">导出</Button>
      </div>
      <div class="query-group" v-if="!more">
        <TimeGroup v-model="createTime" @on-change="setCreateTime"></TimeGroup>
        <Button @click="checkPermission('1096:select', search)">查询</Button>
        <Button @click="more = true">更多查询</Button>
      </div>
    </div>
    <Table
      :columns="columns"
      :data="data"
      stripe
      border
      :height="height"
      @on-selection-change="selection"
      @on-row-dblclick="dblclick"
      :loading="loading"
      @on-sort-change="sort"></Table>
    <Page
      :total="page.total"
      show-elevator
      show-sizer
      show-total
      class-name="page"
      :page-size-opts="page.pageSizePots"
      @on-change="changePage"
      @on-page-size-change="changeNum"
      :current="query.pageNum"></Page>
    <Modal
      v-model="modal.show"
      :title="modal.title"
      :width="600"
      :loading="modal.loading"
      @on-cancel="cancel">
      <Form
        ref="form"
        :model="modal.data"
        :rules="ruleValidate"
        class="layout-form">
        <FormItem label="Rzt202工单号：" prop="fProductionBatchNumber">
          <i-input
            v-model.trim="modal.data.fProductionBatchNumber"
            placeholder="请输入Rzt202工单号"
          />
        </FormItem>
        <FormItem label="成品型号：" prop="fProductModel">
          <i-input
            v-model.trim="modal.data.fProductModel"
            placeholder="请输入成品型号"
          />
        </FormItem>
        <FormItem label="设备序列号：" prop="fDeviceSn">
          <i-input
            v-model.trim="modal.data.fDeviceSn"
            placeholder="请输入设备序列号"
          />
        </FormItem>
        <FormItem label="测试类型，1.前测，2.后测，3.QA测试，4.老化测试：" prop="fTestType">
          <i-input
            v-model.trim="modal.data.fTestType"
            placeholder="请输入测试类型，1.前测，2.后测，3.QA测试，4.老化测试"
          />
        </FormItem>
        <FormItem label="设备测试结果：" prop="fDeviceTestResult">
          <i-input
            v-model.trim="modal.data.fDeviceTestResult"
            placeholder="请输入设备测试结果"
          />
        </FormItem>
        <FormItem label="笔记本CPU型号：" prop="fLaptopCpu">
          <i-input
            v-model.trim="modal.data.fLaptopCpu"
            placeholder="请输入笔记本CPU型号"
          />
        </FormItem>
        <FormItem label="笔记本内存容量：" prop="fLaptopMemory">
          <i-input
            v-model.trim="modal.data.fLaptopMemory"
            placeholder="请输入笔记本内存容量"
          />
        </FormItem>
        <FormItem label="笔记本硬盘容量：" prop="fLaptopDisk">
          <i-input
            v-model.trim="modal.data.fLaptopDisk"
            placeholder="请输入笔记本硬盘容量"
          />
        </FormItem>
        <FormItem label="笔记本主板型号：" prop="fLaptopModel">
          <i-input
            v-model.trim="modal.data.fLaptopModel"
            placeholder="请输入笔记本主板型号"
          />
        </FormItem>
        <FormItem label="笔记本序列号：" prop="fLaptopSerialNo">
          <i-input
            v-model.trim="modal.data.fLaptopSerialNo"
            placeholder="请输入笔记本序列号"
          />
        </FormItem>
        <FormItem label="签名屏开关(1正常 0异常)：" prop="fSignScreenSwitch">
          <i-input
            v-model.trim="modal.data.fSignScreenSwitch"
            placeholder="请输入签名屏开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="签名屏签名(1正常 0异常)：" prop="fSignScreenSign">
          <i-input
            v-model.trim="modal.data.fSignScreenSign"
            placeholder="请输入签名屏签名(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="签名屏签名质量(1正常 0异常)：" prop="fSignScreenQuality">
          <i-input
            v-model.trim="modal.data.fSignScreenQuality"
            placeholder="请输入签名屏签名质量(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="打印机开关(1正常 0异常)：" prop="fPrinterSwitch">
          <i-input
            v-model.trim="modal.data.fPrinterSwitch"
            placeholder="请输入打印机开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="打印机打印(1正常 0异常)：" prop="fPrinterPrint">
          <i-input
            v-model.trim="modal.data.fPrinterPrint"
            placeholder="请输入打印机打印(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="打印机打印质量(1正常 0异常)：" prop="fPrinterQuality">
          <i-input
            v-model.trim="modal.data.fPrinterQuality"
            placeholder="请输入打印机打印质量(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="指纹仪开关(1正常 0异常)：" prop="fFingerprintSwitch">
          <i-input
            v-model.trim="modal.data.fFingerprintSwitch"
            placeholder="请输入指纹仪开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="指纹仪采集(1正常 0异常)：" prop="fFingerprintCollect">
          <i-input
            v-model.trim="modal.data.fFingerprintCollect"
            placeholder="请输入指纹仪采集(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="指纹仪采集质量(1正常 0异常)：" prop="fFingerprintQuality">
          <i-input
            v-model.trim="modal.data.fFingerprintQuality"
            placeholder="请输入指纹仪采集质量(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="指纹仪序列号：" prop="fFingerprintSerialNo">
          <i-input
            v-model.trim="modal.data.fFingerprintSerialNo"
            placeholder="请输入指纹仪序列号"
          />
        </FormItem>
        <FormItem label="高拍仪开关(1正常 0异常)：" prop="fCameraSwitch">
          <i-input
            v-model.trim="modal.data.fCameraSwitch"
            placeholder="请输入高拍仪开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="高拍仪拍摄(1正常 0异常)：" prop="fCameraCapture">
          <i-input
            v-model.trim="modal.data.fCameraCapture"
            placeholder="请输入高拍仪拍摄(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="高拍仪拍摄质量(1正常 0异常)：" prop="fCameraQuality">
          <i-input
            v-model.trim="modal.data.fCameraQuality"
            placeholder="请输入高拍仪拍摄质量(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="副屏厂商型号：" prop="fSubScreenModel">
          <i-input
            v-model.trim="modal.data.fSubScreenModel"
            placeholder="请输入副屏厂商型号"
          />
        </FormItem>
        <FormItem label="副屏分辨率：" prop="fSubScreenResolution">
          <i-input
            v-model.trim="modal.data.fSubScreenResolution"
            placeholder="请输入副屏分辨率"
          />
        </FormItem>
        <FormItem label="电池标称容量：" prop="fBatteryCapacity">
          <i-input
            v-model.trim="modal.data.fBatteryCapacity"
            placeholder="请输入电池标称容量"
          />
        </FormItem>
        <FormItem label="电池总电压：" prop="fBatteryVoltage">
          <i-input
            v-model.trim="modal.data.fBatteryVoltage"
            placeholder="请输入电池总电压"
          />
        </FormItem>
        <FormItem label="电池温度：" prop="fBatteryTemp">
          <i-input
            v-model.trim="modal.data.fBatteryTemp"
            placeholder="请输入电池温度"
          />
        </FormItem>
        <FormItem label="电池循环次数：" prop="fBatteryCycleCount">
          <i-input
            v-model.trim="modal.data.fBatteryCycleCount"
            placeholder="请输入电池循环次数"
          />
        </FormItem>
        <FormItem label="电池放电(1正常 0异常)：" prop="fBatteryDischarge">
          <i-input
            v-model.trim="modal.data.fBatteryDischarge"
            placeholder="请输入电池放电(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="电池充电(1正常 0异常)：" prop="fBatteryCharge">
          <i-input
            v-model.trim="modal.data.fBatteryCharge"
            placeholder="请输入电池充电(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="充电指示灯(1正常 0异常)：" prop="fChargeIndicator">
          <i-input
            v-model.trim="modal.data.fChargeIndicator"
            placeholder="请输入充电指示灯(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="Windows版本：" prop="fWindowsVersion">
          <i-input
            v-model.trim="modal.data.fWindowsVersion"
            placeholder="请输入Windows版本"
          />
        </FormItem>
        <FormItem label="Windows授权：" prop="fWindowsLicense">
          <i-input
            v-model.trim="modal.data.fWindowsLicense"
            placeholder="请输入Windows授权"
          />
        </FormItem>
        <FormItem label="摄像头开关(1正常 0异常)：" prop="fCameraLight">
          <i-input
            v-model.trim="modal.data.fCameraLight"
            placeholder="请输入摄像头开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="摄像头拍摄(1正常 0异常)：" prop="fCameraTakePhoto">
          <i-input
            v-model.trim="modal.data.fCameraTakePhoto"
            placeholder="请输入摄像头拍摄(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="摄像头拍摄质量(1正常 0异常)：" prop="fCameraPhotoQuality">
          <i-input
            v-model.trim="modal.data.fCameraPhotoQuality"
            placeholder="请输入摄像头拍摄质量(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="补光灯红外灯(1正常 0异常)：" prop="fFillLightIr">
          <i-input
            v-model.trim="modal.data.fFillLightIr"
            placeholder="请输入补光灯红外灯(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="补光灯绿灯(1正常 0异常)：" prop="fFillLightGreen">
          <i-input
            v-model.trim="modal.data.fFillLightGreen"
            placeholder="请输入补光灯绿灯(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="补光灯黄灯(1正常 0异常)：" prop="fFillLightWhite">
          <i-input
            v-model.trim="modal.data.fFillLightWhite"
            placeholder="请输入补光灯黄灯(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="补光灯序列号：" prop="fFillLightSerialNo">
          <i-input
            v-model.trim="modal.data.fFillLightSerialNo"
            placeholder="请输入补光灯序列号"
          />
        </FormItem>
        <FormItem label="虹膜设备开关(1正常 0异常)：" prop="fIrisSwitch">
          <i-input
            v-model.trim="modal.data.fIrisSwitch"
            placeholder="请输入虹膜设备开关(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="虹膜采集(1正常 0异常)：" prop="fIrisCollect">
          <i-input
            v-model.trim="modal.data.fIrisCollect"
            placeholder="请输入虹膜采集(1正常 0异常)"
          />
        </FormItem>
        <FormItem label="虹膜采集质量：" prop="fIrisQuality">
          <i-input
            v-model.trim="modal.data.fIrisQuality"
            placeholder="请输入虹膜采集质量"
          />
        </FormItem>
        <FormItem label="虹膜序列号：" prop="fIrisSn">
          <i-input
            v-model.trim="modal.data.fIrisSn"
            placeholder="请输入虹膜序列号"
          />
        </FormItem>
        <FormItem label="FC300喇叭播放：" prop="fSpeakerPlay">
          <i-input
            v-model.trim="modal.data.fSpeakerPlay"
            placeholder="请输入FC300喇叭播放"
          />
        </FormItem>
        <FormItem label="操作员：" prop="fOperator">
          <i-input
            v-model.trim="modal.data.fOperator"
            placeholder="请输入操作员"
          />
        </FormItem>
        <FormItem label="操作时间：" prop="fOperateTime">
          <i-input
            v-model.trim="modal.data.fOperateTime"
            placeholder="请输入操作时间"
          />
        </FormItem>
        <FormItem label="操作地点：" prop="fOperateLocation">
          <i-input
            v-model.trim="modal.data.fOperateLocation"
            placeholder="请输入操作地点"
          />
        </FormItem>
        <FormItem label="MAC地址：" prop="fMacAddress">
          <i-input
            v-model.trim="modal.data.fMacAddress"
            placeholder="请输入MAC地址"
          />
        </FormItem>
        <FormItem label="IP地址：" prop="fIpAddress">
          <i-input
            v-model.trim="modal.data.fIpAddress"
            placeholder="请输入IP地址"
          />
        </FormItem>
        <FormItem label="更新时间：" prop="fUpdateTime">
          <i-input
            v-model.trim="modal.data.fUpdateTime"
            placeholder="请输入更新时间"
          />
        </FormItem>
      </Form>
      <div slot="footer">
        <Button type="warning" @click="confirm">确定</Button>
        <Button type="default" @click="cancel">退出</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import {checkUnusualChar} from "../../utils/validate";
import SelectWithPage from "../../components/SelectWithPage";
import TimeGroup from "../../components/TimeGroup.vue";

export default {
  name: "Rzt202",
  components: {
    TimeGroup,
    SelectWithPage,
  },
  data() {
    return {
      data: [],
      columns: [],
      page: {
        pageNum: 1, //当前页
        total: 0, //数据总数
        pageSize: 10, //每页显示记录数
        pageSizePots: [10, 30, 50, 100], //页码配置
      },
      query: {
        pageNum: 1,
        pageSize: 10,
      },
      height: "",
      ids: [],
      row: {},
      uploadHeader: {
        Authorization: sessionStorage.token,
      },
      modal: {
        show: false,
        title: "",
        loading: false,
        data: {},
      },
      ruleValidate: {
        fNumber: [{
          required: true,
          message: '数据项不得为空！',
          trigger: 'change'
        }, {
          type: 'string',
          max: 100,
          message: '最大长度不能超过100个字符！',
          trigger: 'change'
        }, {
          validator: checkUnusualChar,
          trigger: 'change'
        }],
        fName: [{
          required: true,
          message: '数据项不得为空！',
          trigger: 'change'
        }, {
          type: 'string',
          max: 100,
          message: '最大长度不能超过100个字符！',
          trigger: 'change'
        }, {
          validator: checkUnusualChar,
          trigger: 'change'
        }],
      },
      loading: true,
      more: false,
      queryExcel: {},
      createTime: [],
      testType: {
        1: '前测',
        2: '后测',
        3: 'QA测试',
        4: '老化测试',
      }
    };
  },
  watch: {
    more(value) {
      this.resetHeight()
    },
  },
  mounted() {
    this.init();
    this.checkPermission("1096:select", this.search);
    this.$nextTick(() => {
      this.resetHeight()
    });
    window.onresize = () => {
      this.resetHeight()
    };
  },
  computed: {},
  methods: {
    resetHeight() {
      this.height = this.$refs.container.clientHeight - (this.more ? 277 : 150);
    },
    init() {
      this.columns = [
        {
          key: "fID",
          type: "selection",
          width: 60,
          fixed: "left",
        },
        {
          title: "序号",
          key: "fID",
          width: 80,
          align: "center",
          render: (h, params) => {
            return h(
              "span",
              params.index + (this.query.pageNum - 1) * this.query.pageSize + 1
            );
          },
        },
        {
          title: "音频老化总次数",
          key: "fAudioCount",
          width: 170,
        },

      ];
    },
    // 表单选择分类
    setProduct(data) {
      this.modal.data.fProductID = data ? data.value : ''
      this.modal.data.fProductName = data ? data.label : ''
    },
    //表单选择客户
    setCustomer(data) {
      this.modal.data.fCustomerID = data ? data.value : ''
      this.modal.data.fCustomerName = data ? data.label : ''
    },
    //获取列表
    getList(data) {
      const api = {
        url: "/ipcAgingTest/selectPageList",
        method: "post",
        data: data,
      };
      this.loading = true;
      this.$api(api)
        .then((response) => {
          this.loading = false;
          if (response.data.code === "0") {
            this.data = response.data.data.list;
            this.page.total = response.data.data.total;
          } else {
            this.$Message.error(response.data.message);
          }
        })
        .catch((error) => {
          this.loading = false;
          this.$Message.error(error.response.data.message);
        });
    },
    //导入
    importExcel() {
      this.$ImportModal({
        templateName: this.$route.meta.title + '_导入模板.xlsx',
        action: this.M.rzt202Import,
        templateUrl: '/template/excel/rzt202.xlsx',
        exitMethod: () => {
          this.search();
        }
      })
    },
    //切换页码
    changePage(pageNum) {
      this.query.pageNum = pageNum;
      this.getList(this.query);
    },
    //切换每页显示条数
    changeNum(pageSize) {
      this.query.pageSize = pageSize;
      this.getList(this.query);
    },
    //创建时间段
    setCreateTime(data) {
      this.query.queryCreateTimeStart = data[0];
      this.query.queryCreateTimeEnd = data[1];
    },
    //查询
    search() {
      this.getList(this.query);
      this.queryExcel = this.query;
      this.ids = [];
      this.row = {};
    },
    //重置
    reset() {
      this.queryExcel = {};
      this.query = {
        pageNum: this.page.pageNum,
        pageSize: this.page.pageSize,
      };
      this.search();
    },
    //新增
    add() {
      this.modal = {
        show: true,
        title: "新增",
        data: {},
      };
    },
    //更新
    update() {
      if (this.ids.length !== 1) {
        this.$Message.error("修改操作，只能选中一条数据进行操作！");
        return;
      }
      this.modal = {
        show: true,
        title: "修改",
        data: this.row,
      };
    },
    //确认
    confirm() {
      this.$refs.form.validate((valid) => {
        if (!valid) {
          this.$nextTick(() => {
            this.modal.show = true;
            this.modal.loading = false;
          });
          return;
        }
        this.modal.loading = true;
        const api = {
          url:
            this.modal.title === "修改"
              ? "/rzt202/update"
              : "/rzt202/insert",
          method: "post",
          data: this.modal.data,
        };
        this.$api(api)
          .then((response) => {
            this.modal.loading = false;
            if (response.data.code === "0") {
              this.modal.show = false;
              this.modal.data = {};
              this.$refs.form.resetFields();
              this.search();
              this.$Message.success(response.data.message);
            } else {
              this.$Message.error(response.data.message);
            }
          })
          .catch((error) => {
            this.$Message.error(error.response.data.message);
          });
      });
    },
    //退出
    cancel() {
      this.$refs.form.resetFields();
      this.modal.show = false;
      this.modal.data = {};
    },
    //双击事件
    dblclick(data, index) {
      this.checkPermission("1096:update", () => {
        this.modal = {
          show: true,
          title: "修改",
          loading: false,
          data,
        };
      });
    },
    //选择行数据
    selection(data) {
      this.ids = data.map((item) => {
        return item.fID;
      });
      this.row = data.length === 1 ? data[0] : {};
    },
    //删除
    batchDel() {
      if (this.ids.length === 0) {
        this.$Message.error("删除操作，请至少选中一条数据进行操作！");
        return;
      }
      this.$Modal.confirm({
        title: "确定要删除所选中项吗？",
        loading: true,
        onOk: () => {
          const api = {
            url: "/rzt202/batchDelete",
            method: "post",
            data: this.ids,
          };
          this.$api(api)
            .then((response) => {
              this.$Modal.remove();
              if (response.data.code === "0") {
                this.$Message.success(response.data.message);
              } else {
                this.$Message.error(response.data.message);
              }
              this.search();
            })
            .catch((error) => {
              this.$Modal.remove();
              this.$Message.error(error.response.data.message);
            });
        },
      });
    },
    enable() {
      this.changeStatus("1");
    },
    disable() {
      this.changeStatus("2");
    },
    //改变状态
    changeStatus(fStatus) {
      const text = fStatus === "1" ? "启用" : "禁用";
      if (this.ids.length === 0) {
        this.$Message.error(text + "操作，请至少选中一条数据进行操作！");
        return;
      }
      const data = {
        ids: this.ids.join(","),
        fStatus,
      };
      this.$Modal.confirm({
        title: "确定要" + text + "所选中项吗？",
        loading: true,
        onOk: () => {
          const api = {
            url: "/rzt202/changeStatus",
            method: "post",
            data: this.$qs.stringify(data),
          };
          this.$api(api)
            .then((response) => {
              this.$Modal.remove();
              if (response.data.code === "0") {
                this.$Message.success(response.data.message);
              } else {
                this.$Message.error(response.data.message);
              }
              this.search();
            })
            .catch((error) => {
              this.$Modal.remove();
              this.$Message.error(error.response.data.message);
            });
        },
      });
    },
    //导出
    exportExcel() {
      if (this.page.total === 0) {
        this.$Message.error("没有要导出的数据！");
        return;
      }
      if (this.page.total > 10000) {
        this.$Message.error("最多可导出10000条记录！");
        return;
      }
      const api = {
        url: "/rzt202/export",
        method: "post",
        data: this.queryExcel,
        responseType: "arraybuffer",
      };
      this.$api(api)
        .then((response) => {
          if (response.status === 200) {
            let blob = new Blob([response.data], {
              type:
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8",
            });
            this.$store.commit("download", {
              blob,
              title: this.$route.meta.title + "_" + this.dateFormat(),
            });
          } else {
            this.$Message.error("系统异常，请联系管理员！");
          }
        })
        .catch((error) => {
          console.error(error);
          this.$Message.error("系统异常，请联系管理员！");
        });
    },
    //获取日期
    dateFormat(date = new Date()) {
      let year = date.getFullYear(),
        month = date.getMonth() + 1,
        day = date.getDate();
      return [year, month, day].join("-");
    },
    //排序
    sort(data) {
      if (data.order === "normal") {
        return;
      }
      this.query.sortParams = {};
      this.query.sortParams[data.key] = data.order;
      this.search();
    },
  },
}
</script>

<style scoped>

</style>
