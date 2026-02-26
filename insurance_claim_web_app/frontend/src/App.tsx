import React, { useState } from 'react';
import { Layout, Menu, theme, Button, Upload, message, Table, Card, Steps, Result } from 'antd';
import { UploadOutlined, SolutionOutlined, UserOutlined, ShopOutlined, AppstoreOutlined, AuditOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import type { TableColumnsType } from 'antd';

const { Header, Content, Footer, Sider } = Layout;

// 定义理赔数据类型
interface ClaimData {
  id: string;
  documentName: string;
  documentType: string;
  status: string;
  uploadTime: string;
}

// 定义提取字段类型
interface ExtractedField {
  fieldName: string;
  fieldValue: string;
  confidence: number;
}

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [claimData, setClaimData] = useState<ClaimData[]>([]);
  const [extractedFields, setExtractedFields] = useState<ExtractedField[]>([]);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [processing, setProcessing] = useState(false);

  const {
    token: { colorBgContainer },
  } = theme.useToken();

  // 上传文件处理
  const handleUpload: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  // 开始处理理赔
  const handleProcessClaim = () => {
    if (fileList.length === 0) {
      message.warning('请先上传理赔文档');
      return;
    }

    setProcessing(true);
    
    // 模拟处理过程
    setTimeout(() => {
      // 模拟上传文档数据
      const mockClaimData: ClaimData[] = fileList.map((file, index) => ({
        id: `doc-${index}`,
        documentName: file.name || '未知文件',
        documentType: ['病历', '发票', '身份证明'][index % 3],
        status: '已分类',
        uploadTime: new Date().toLocaleString()
      }));
      
      setClaimData(mockClaimData);
      
      // 模拟提取的字段
      const mockExtractedFields: ExtractedField[] = [
        { fieldName: '患者姓名', fieldValue: '张三', confidence: 0.98 },
        { fieldName: '诊断结果', fieldValue: '急性阑尾炎', confidence: 0.95 },
        { fieldName: '入院日期', fieldValue: '2023-10-05', confidence: 0.92 },
        { fieldName: '出院日期', fieldValue: '2023-10-10', confidence: 0.94 },
        { fieldName: '发票金额', fieldValue: '¥5,000.00', confidence: 0.97 },
        { fieldName: '发票号码', fieldValue: '12345678', confidence: 0.99 }
      ];
      
      setExtractedFields(mockExtractedFields);
      
      setProcessing(false);
      setActiveStep(3); // 设置为完成步骤
      
      message.success('理赔处理完成！');
    }, 3000);
  };

  // 重置处理
  const handleReset = () => {
    setClaimData([]);
    setExtractedFields([]);
    setFileList([]);
    setActiveStep(0);
  };

  // 菜单项
  const items = [
    { label: '理赔上传', key: '1', icon: <UploadOutlined /> },
    { label: '案件处理', key: '2', icon: <SolutionOutlined /> },
    { label: '核赔审核', key: '3', icon: <AuditOutlined /> },
    { label: '客户管理', key: '4', icon: <UserOutlined /> },
    { label: '产品管理', key: '5', icon: <ShopOutlined /> },
    { label: '报表统计', key: '6', icon: <AppstoreOutlined /> },
  ];

  // 文档表格列定义
  const columns: TableColumnsType<ClaimData> = [
    { title: '文档名称', dataIndex: 'documentName', key: 'documentName' },
    { title: '文档类型', dataIndex: 'documentType', key: 'documentType' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    { title: '上传时间', dataIndex: 'uploadTime', key: 'uploadTime' },
  ];

  // 字段表格列定义
  const fieldColumns: TableColumnsType<ExtractedField> = [
    { title: '字段名称', dataIndex: 'fieldName', key: 'fieldName' },
    { title: '字段值', dataIndex: 'fieldValue', key: 'fieldValue' },
    { 
      title: '置信度', 
      dataIndex: 'confidence', 
      key: 'confidence',
      render: (text: number) => `${(text * 100).toFixed(1)}%`
    },
  ];

  // 步骤条数据
  const steps = [
    { title: '上传文档', description: '上传理赔相关文档' },
    { title: '文档分类', description: 'AI自动分类文档类型' },
    { title: '信息提取', description: '提取关键信息字段' },
    { title: '责任评估', description: '评估理赔责任' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" />
        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }} />
        <Content style={{ margin: '16px' }}>
          <Card title="智能理赔助手" style={{ marginBottom: 16 }}>
            <Steps 
              current={activeStep} 
              items={steps.map(item => ({ ...item, key: item.title }))} 
              style={{ marginBottom: 24 }}
            />
            
            {/* 上传区域 */}
            {!processing && activeStep < 3 && (
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <Upload
                  fileList={fileList}
                  onChange={handleUpload}
                  multiple
                  beforeUpload={() => false} // 阻止自动上传，我们需要手动处理
                >
                  <Button icon={<UploadOutlined />}>点击上传理赔文档</Button>
                </Upload>
                <div style={{ marginTop: 16 }}>
                  <Button 
                    type="primary" 
                    onClick={handleProcessClaim}
                    disabled={fileList.length === 0}
                    loading={processing}
                  >
                    开始处理理赔
                  </Button>
                </div>
              </div>
            )}
            
            {/* 处理中状态 */}
            {processing && (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <h3>正在处理理赔文档...</h3>
                <p>AI正在分析您上传的文档，请稍候...</p>
              </div>
            )}
            
            {/* 结果展示 */}
            {activeStep >= 3 && !processing && (
              <>
                <Card title="文档处理结果" style={{ marginBottom: 16 }}>
                  <Table 
                    dataSource={claimData} 
                    columns={columns} 
                    rowKey="id"
                    pagination={{ pageSize: 5 }}
                  />
                </Card>
                
                <Card title="提取的关键信息" style={{ marginBottom: 16 }}>
                  <Table 
                    dataSource={extractedFields} 
                    columns={fieldColumns} 
                    rowKey="fieldName"
                    pagination={{ pageSize: 10 }}
                  />
                </Card>
                
                <Card title="理赔评估结果">
                  <Result
                    status="success"
                    title="理赔责任评估完成"
                    subTitle="根据AI分析，该理赔案件符合保险责任范围"
                    extra={[
                      <Button type="primary" key="console">
                        查看详细报告
                      </Button>,
                      <Button key="reset" onClick={handleReset}>
                        重新处理
                      </Button>,
                    ]}
                  />
                </Card>
              </>
            )}
          </Card>
        </Content>
        <Footer style={{ textAlign: 'center' }}>保险理赔助手 ©2023 Created by Insurance Tech Team</Footer>
      </Layout>
    </Layout>
  );
};

export default App;