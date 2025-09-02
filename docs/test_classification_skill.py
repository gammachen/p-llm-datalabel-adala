#!/usr/bin/env python3
"""
ClassificationSkill 功能测试脚本

这个脚本演示了如何使用ClassificationSkill进行文本分类任务，
包括基础分类、自定义配置和错误处理。
"""

import os
import sys
from typing import List
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adala.skills.collection.classification import ClassificationSkill
from adala.utils.internal_data import InternalDataFrame

# 模拟运行时（实际使用时需要真实的运行时）
class MockRuntime:
    """模拟运行时用于测试"""
    
    def __init__(self, responses: List[str] = None):
        self.responses = responses or ["positive", "negative", "neutral"]
        self.call_count = 0
    
    def batch_to_batch(self, input_df, **kwargs):
        """模拟批量处理"""
        self.call_count += 1
        print(f"MockRuntime: Processing {len(input_df)} items")
        
        # 模拟分类结果
        predictions = []
        for i, _ in enumerate(input_df):
            pred = self.responses[i % len(self.responses)]
            predictions.append(pred)
        
        result_df = input_df.copy()
        result_df['predictions'] = predictions
        return result_df

class MockAsyncRuntime:
    """模拟异步运行时"""
    
    async def batch_to_batch(self, input_df, **kwargs):
        """模拟异步批量处理"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        # 模拟分类结果
        predictions = ["positive", "negative", "neutral"] * (len(input_df) // 3 + 1)
        predictions = predictions[:len(input_df)]
        
        result_df = input_df.copy()
        result_df['predictions'] = predictions
        return result_df

def test_basic_classification():
    """测试基础分类功能"""
    print("=" * 50)
    print("测试1: 基础分类功能")
    print("=" * 50)
    
    # 创建分类技能
    skill = ClassificationSkill(
        labels=["positive", "negative", "neutral"]
    )
    
    print("✅ 成功创建基础分类技能")
    print(f"技能名称: {skill.name}")
    print(f"分类标签: {skill.labels}")
    print(f"指令: {skill.instructions}")
    
    # 测试输入字段
    input_fields = skill.get_input_fields()
    print(f"输入字段: {input_fields}")
    
    # 测试输出字段
    output_fields = skill.get_output_fields()
    print(f"输出字段: {output_fields}")

def test_custom_schema():
    """测试自定义Schema配置"""
    print("\n" + "=" * 50)
    print("测试2: 自定义Schema配置")
    print("=" * 50)
    
    # 使用field_schema配置
    skill = ClassificationSkill(
        field_schema={
            "predictions": {
                "type": "string",
                "description": "Email classification",
                "enum": ["spam", "ham"]
            }
        },
        name="spam_detector",
        instructions="Classify emails as spam or legitimate"
    )
    
    print("✅ 成功创建自定义Schema技能")
    print(f"技能名称: {skill.name}")
    print(f"分类类型: {skill.field_schema['predictions']['enum']}")
    print(f"指令: {skill.instructions}")

def test_template_customization():
    """测试模板自定义"""
    print("\n" + "=" * 50)
    print("测试3: 模板自定义")
    print("=" * 50)
    
    skill = ClassificationSkill(
        labels=["urgent", "high", "medium", "low"],
        input_template="Task: {text}",
        output_template="Priority: {predictions}",
        instructions="Classify task priority based on urgency",
        name="priority_classifier"
    )
    
    print("✅ 成功创建自定义模板技能")
    print(f"输入模板: {skill.input_template}")
    print(f"输出模板: {skill.output_template}")
    print(f"完整指令: {skill.instructions}")

def test_mock_processing():
    """测试模拟处理流程"""
    print("\n" + "=" * 50)
    print("测试4: 模拟处理流程")
    print("=" * 50)
    
    # 创建技能和模拟数据
    skill = ClassificationSkill(
        labels=["positive", "negative", "neutral"]
    )
    
    # 创建测试数据
    test_data = InternalDataFrame({
        'input': [
            "I love this product! It's amazing!",
            "This is the worst experience ever",
            "It's okay, nothing special",
            "Absolutely fantastic quality",
            "Terrible customer service"
        ]
    })
    
    print("测试数据:")
    for i, text in enumerate(test_data['input']):
        print(f"  {i+1}. {text}")
    
    # 使用模拟运行时处理
    mock_runtime = MockRuntime()
    result = skill.apply(test_data, mock_runtime)
    
    print("\n处理结果:")
    for i, (text, pred) in enumerate(zip(result['input'], result['predictions'])):
        print(f"  {i+1}. {text[:30]}... -> {pred}")
    
    print(f"调用次数: {mock_runtime.call_count}")

async def test_async_processing():
    """测试异步处理"""
    print("\n" + "=" * 50)
    print("测试5: 异步处理")
    print("=" * 50)
    
    skill = ClassificationSkill(
        labels=["tech", "sports", "politics", "entertainment"]
    )
    
    test_data = InternalDataFrame({
        'input': [
            "New iPhone released with AI features",
            "Championship game ends in overtime",
            "Election results announced today",
            "New movie breaks box office records"
        ]
    })
    
    print("异步处理数据...")
    mock_async_runtime = MockAsyncRuntime()
    result = await skill.aapply(test_data, mock_async_runtime)
    
    print("异步处理完成:")
    for text, pred in zip(result['input'], result['predictions']):
        print(f"  {text[:30]}... -> {pred}")

def test_error_cases():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("测试6: 错误处理")
    print("=" * 50)
    
    try:
        # 测试无配置错误
        skill = ClassificationSkill()
        print("❌ 应该抛出配置错误")
    except Exception as e:
        print(f"✅ 正确捕获配置错误: {type(e).__name__}")
    
    try:
        # 测试无效标签
        skill = ClassificationSkill(
            labels=[]  # 空标签列表
        )
        print("❌ 应该抛出标签错误")
    except Exception as e:
        print(f"✅ 正确捕获标签错误: {type(e).__name__}")

def test_skill_properties():
    """测试技能属性"""
    print("\n" + "=" * 50)
    print("测试7: 技能属性检查")
    print("=" * 50)
    
    skill = ClassificationSkill(
        labels=["A", "B", "C"],
        name="test_classifier"
    )
    
    print("技能属性:")
    print(f"  类型: {type(skill).__name__}")
    print(f"  名称: {skill.name}")
    print(f"  是否冻结: {skill.frozen}")
    print(f"  指令优先: {skill.instructions_first}")
    print(f"  响应模型: {skill.response_model}")
    
    # 检查继承关系
    print(f"\n继承关系:")
    print(f"  是Skill子类: {issubclass(type(skill), skill.__class__.__bases__[0])}")
    print(f"  基类: {skill.__class__.__bases__[0].__name__}")

def main():
    """主测试函数"""
    print("ClassificationSkill 功能测试")
    print("=" * 60)
    
    # 运行所有测试
    test_basic_classification()
    test_custom_schema()
    test_template_customization()
    test_mock_processing()
    
    # 异步测试
    asyncio.run(test_async_processing())
    
    test_error_cases()
    test_skill_properties()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)
    
    # 使用建议
    print("\n📋 使用建议:")
    print("1. 始终提供labels或field_schema")
    print("2. 根据任务调整instructions")
    print("3. 使用异步处理提高效率")
    print("4. 监控API调用成本")
    print("5. 收集反馈改进技能")

if __name__ == "__main__":
    main()