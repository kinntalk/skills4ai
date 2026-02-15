import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class UsageVisualizer:
    def __init__(self, stats_file: str = None):
        if stats_file is None:
            self.stats_file = Path(__file__).parent.parent / "skill_usage_stats.json"
        else:
            self.stats_file = Path(stats_file)
        
        self.stats_data = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        if not self.stats_file.exists():
            return {
                "version": "1.0.0",
                "last_updated": None,
                "skills": {}
            }
        
        with open(self.stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_usage_chart(self, limit: int = 10, output_file: str = None) -> str:
        skills_list = []
        
        for skill_name, stats in self.stats_data["skills"].items():
            skills_list.append({
                "name": skill_name,
                "invocations": stats["invocations"]
            })
        
        skills_list.sort(key=lambda x: x["invocations"], reverse=True)
        top_skills = skills_list[:limit]
        
        if not top_skills:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        names = [skill["name"] for skill in top_skills]
        invocations = [skill["invocations"] for skill in top_skills]
        
        bars = ax.barh(range(len(names)), invocations, color='steelblue', edgecolor='navy', alpha=0.8)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel('调用次数', fontsize=12, fontweight='bold')
        ax.set_title(f'技能使用频率 TOP {limit}', fontsize=14, fontweight='bold', pad=20)
        
        for i, (bar, count) in enumerate(zip(bars, invocations)):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                   str(count), va='center', fontsize=10, fontweight='bold')
        
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if output_file is None:
            output_dir = Path(__file__).parent.parent / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"usage_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file)

    def generate_success_rate_chart(self, limit: int = 10, output_file: str = None) -> str:
        skills_list = []
        
        for skill_name, stats in self.stats_data["skills"].items():
            total = stats["success_count"] + stats["failure_count"]
            if total > 0:
                success_rate = (stats["success_count"] / total) * 100
                skills_list.append({
                    "name": skill_name,
                    "success_rate": success_rate,
                    "invocations": stats["invocations"]
                })
        
        skills_list.sort(key=lambda x: x["success_rate"], reverse=True)
        top_skills = skills_list[:limit]
        
        if not top_skills:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        names = [skill["name"] for skill in top_skills]
        success_rates = [skill["success_rate"] for skill in top_skills]
        
        colors = ['#2ecc71' if rate >= 80 else '#f39c12' if rate >= 60 else '#e74c3c' 
                 for rate in success_rates]
        
        bars = ax.barh(range(len(names)), success_rates, color=colors, edgecolor='black', alpha=0.8)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel('成功率 (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'技能成功率 TOP {limit}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 100)
        
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   f'{rate:.1f}%', va='center', fontsize=10, fontweight='bold')
        
        ax.axvline(x=80, color='green', linestyle='--', alpha=0.5, label='优秀 (80%)')
        ax.axvline(x=60, color='orange', linestyle='--', alpha=0.5, label='及格 (60%)')
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if output_file is None:
            output_dir = Path(__file__).parent.parent / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"success_rate_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file)

    def generate_trend_chart(self, skill: str, output_file: str = None) -> str:
        if skill not in self.stats_data["skills"]:
            return None
        
        skill_stats = self.stats_data["skills"][skill]
        history = skill_stats.get("execution_history", [])
        
        if not history or len(history) < 2:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        timestamps = []
        execution_times = []
        success_values = []
        
        for record in history:
            try:
                ts = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                timestamps.append(ts)
                execution_times.append(record["execution_time"])
                success_values.append(1 if record["success"] else 0)
            except:
                continue
        
        if not timestamps:
            return None
        
        ax1.plot(timestamps, execution_times, marker='o', linewidth=2, markersize=6, 
                color='steelblue', label='执行时间')
        ax1.set_xlabel('时间', fontsize=12, fontweight='bold')
        ax1.set_ylabel('执行时间 (秒)', fontsize=12, fontweight='bold')
        ax1.set_title(f'{skill} - 执行时间趋势', fontsize=14, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend()
        
        avg_time = sum(execution_times) / len(execution_times)
        ax1.axhline(y=avg_time, color='red', linestyle='--', alpha=0.7, 
                   label=f'平均时间: {avg_time:.2f}秒')
        ax1.legend()
        
        success_count = sum(success_values)
        success_rate = (success_count / len(success_values)) * 100
        
        ax2.plot(timestamps, success_values, marker='s', linewidth=2, markersize=8, 
                color='green', label='成功/失败')
        ax2.set_xlabel('时间', fontsize=12, fontweight='bold')
        ax2.set_ylabel('执行结果', fontsize=12, fontweight='bold')
        ax2.set_title(f'{skill} - 执行结果趋势 (成功率: {success_rate:.1f}%)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['失败', '成功'])
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend()
        
        plt.tight_layout()
        
        if output_file is None:
            output_dir = Path(__file__).parent.parent / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"trend_chart_{skill}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file)

    def generate_comprehensive_report(self, output_file: str = None) -> str:
        if output_file is None:
            output_dir = Path(__file__).parent.parent / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        skills_list = []
        for skill_name, stats in self.stats_data["skills"].items():
            total = stats["success_count"] + stats["failure_count"]
            success_rate = (stats["success_count"] / total * 100) if total > 0 else 0
            skills_list.append({
                "name": skill_name,
                "invocations": stats["invocations"],
                "success_rate": success_rate,
                "avg_time": stats["total_execution_time"] / stats["invocations"] if stats["invocations"] > 0 else 0
            })
        
        skills_list.sort(key=lambda x: x["invocations"], reverse=True)
        top_skills = skills_list[:10]
        
        ax1 = fig.add_subplot(gs[0, 0])
        names = [skill["name"] for skill in top_skills]
        invocations = [skill["invocations"] for skill in top_skills]
        bars = ax1.barh(range(len(names)), invocations, color='steelblue', alpha=0.8)
        ax1.set_yticks(range(len(names)))
        ax1.set_yticklabels(names, fontsize=8)
        ax1.set_xlabel('调用次数', fontsize=10, fontweight='bold')
        ax1.set_title('技能使用频率 TOP 10', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        ax2 = fig.add_subplot(gs[0, 1])
        skills_list.sort(key=lambda x: x["success_rate"], reverse=True)
        top_success = skills_list[:10]
        names2 = [skill["name"] for skill in top_success]
        rates = [skill["success_rate"] for skill in top_success]
        colors2 = ['#2ecc71' if r >= 80 else '#f39c12' if r >= 60 else '#e74c3c' for r in rates]
        bars2 = ax2.barh(range(len(names2)), rates, color=colors2, alpha=0.8)
        ax2.set_yticks(range(len(names2)))
        ax2.set_yticklabels(names2, fontsize=8)
        ax2.set_xlabel('成功率 (%)', fontsize=10, fontweight='bold')
        ax2.set_title('技能成功率 TOP 10', fontsize=12, fontweight='bold')
        ax2.set_xlim(0, 100)
        ax2.grid(axis='x', alpha=0.3)
        
        ax3 = fig.add_subplot(gs[1, 0])
        skills_list.sort(key=lambda x: x["avg_time"])
        fastest = skills_list[:10]
        names3 = [skill["name"] for skill in fastest]
        times = [skill["avg_time"] for skill in fastest]
        bars3 = ax3.barh(range(len(names3)), times, color='lightcoral', alpha=0.8)
        ax3.set_yticks(range(len(names3)))
        ax3.set_yticklabels(names3, fontsize=8)
        ax3.set_xlabel('平均执行时间 (秒)', fontsize=10, fontweight='bold')
        ax3.set_title('执行最快技能 TOP 10', fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        ax4 = fig.add_subplot(gs[1, 1])
        total_invocations = sum(s["invocations"] for s in skills_list)
        total_success = sum(s["success_count"] for s in self.stats_data["skills"].values())
        total_failures = sum(s["failure_count"] for s in self.stats_data["skills"].values())
        overall_rate = (total_success / (total_success + total_failures) * 100) if (total_success + total_failures) > 0 else 0
        
        stats_text = f"""
        总体统计
        {'='*30}
        
        总技能数: {len(self.stats_data['skills'])}
        总调用次数: {total_invocations}
        成功次数: {total_success}
        失败次数: {total_failures}
        整体成功率: {overall_rate:.2f}%
        
        最后更新: {self.stats_data.get('last_updated', 'N/A')}
        """
        ax4.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax4.axis('off')
        ax4.set_title('统计摘要', fontsize=12, fontweight='bold')
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file)


def generate_usage_chart(limit: int = 10, output_file: str = None) -> str:
    visualizer = UsageVisualizer()
    return visualizer.generate_usage_chart(limit, output_file)


def generate_success_rate_chart(limit: int = 10, output_file: str = None) -> str:
    visualizer = UsageVisualizer()
    return visualizer.generate_success_rate_chart(limit, output_file)


def generate_trend_chart(skill: str, output_file: str = None) -> str:
    visualizer = UsageVisualizer()
    return visualizer.generate_trend_chart(skill, output_file)


def generate_comprehensive_report(output_file: str = None) -> str:
    visualizer = UsageVisualizer()
    return visualizer.generate_comprehensive_report(output_file)