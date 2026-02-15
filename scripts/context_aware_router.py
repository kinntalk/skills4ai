import json
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class Phase(Enum):
    IDEATION = "ideation"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    VERIFICATION = "verification"
    MANAGEMENT = "management"
    DOMAIN = "domain"
    GENERATION = "generation"


@dataclass
class ContextInfo:
    phase: Phase
    confidence: float
    keywords: List[str]
    detected_intents: List[str]


@dataclass
class SkillRecommendation:
    skill_name: str
    priority: int
    required_for: List[str]
    confidence: float
    reason: str


@dataclass
class ConflictInfo:
    conflict_type: str
    skills: List[str]
    description: str
    resolution: str


@dataclass
class RoutingDecision:
    user_input: str
    matched_type: str
    candidates: List[Dict]
    selected_skill: Optional[str]
    priority: int
    confidence: float
    conflicts: List[ConflictInfo]
    resolution_strategy: Optional[str]
    timestamp: str
    feedback_history: List[Dict]


class ContextAwareRouter:
    def __init__(self, skill_map_path: str = None):
        if skill_map_path is None:
            skill_map_path = "D:/workspace1/yusuan/.trae/skills/skill_map.json"
        
        self.skill_map_path = skill_map_path
        self.skill_map = self._load_skill_map()
        self.skills = self.skill_map.get("skills", {})
        self.detection_rules = self.skill_map.get("detection_rules", {})
        
        self.phase_keywords = {
            Phase.IDEATION: [
                "brainstorm", "idea", "creative", "explore", "concept",
                "头脑风暴", "创意", "探索", "概念"
            ],
            Phase.PLANNING: [
                "plan", "planning", "spec", "requirements", "architecture",
                "计划", "规划", "规格", "需求", "架构"
            ],
            Phase.IMPLEMENTATION: [
                "implement", "code", "develop", "build", "feature",
                "实现", "编码", "开发", "构建", "功能"
            ],
            Phase.DEBUGGING: [
                "debug", "bug", "fix", "error", "issue", "troubleshoot", "problem",
                "调试", "修复", "错误", "问题", "故障排除"
            ],
            Phase.VERIFICATION: [
                "verify", "test", "review", "check", "validate", "complete", "done", "merge",
                "验证", "测试", "审查", "检查", "完成", "合并"
            ],
            Phase.MANAGEMENT: [
                "skill", "install", "manage", "create skill", "package", "workflow", "template",
                "技能", "安装", "管理", "创建技能", "打包", "工作流", "模板"
            ],
            Phase.DOMAIN: [
                "ui", "ux", "product", "behavioral", "psychology",
                "界面", "交互", "产品", "行为", "心理学"
            ],
            Phase.GENERATION: [
                "generate", "image", "pdf", "render", "convert",
                "生成", "图片", "pdf", "渲染", "转换"
            ]
        }
    
    def _load_skill_map(self) -> Dict:
        try:
            with open(self.skill_map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading skill map: {e}")
            return {}
    
    def detect_context_from_user_input(self, user_input: str) -> ContextInfo:
        user_input_lower = user_input.lower()
        
        phase_scores = {}
        detected_keywords = {phase: [] for phase in Phase}
        
        for phase, keywords in self.phase_keywords.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    score += 1
                    found_keywords.append(keyword)
            
            if found_keywords:
                phase_scores[phase] = score
                detected_keywords[phase] = found_keywords
        
        if not phase_scores:
            return ContextInfo(
                phase=Phase.IMPLEMENTATION,
                confidence=0.3,
                keywords=[],
                detected_intents=["default"]
            )
        
        best_phase = max(phase_scores.items(), key=lambda x: x[1])[0]
        max_score = phase_scores[best_phase]
        total_score = sum(phase_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        detected_intents = []
        for keyword in detected_keywords[best_phase]:
            detected_intents.append(f"{best_phase.value}:{keyword}")
        
        return ContextInfo(
            phase=best_phase,
            confidence=confidence,
            keywords=detected_keywords[best_phase],
            detected_intents=detected_intents
        )
    
    def detect_phase_from_context(self, context: Dict) -> Phase:
        trigger_phase = context.get("trigger_phase")
        if trigger_phase:
            try:
                return Phase(trigger_phase)
            except ValueError:
                pass
        
        required_for = context.get("required_for", [])
        if required_for:
            for req in required_for:
                if "ideation" in req or "idea" in req or "creative" in req or "creation" in req or "component-building" in req:
                    return Phase.IDEATION
                elif "plan" in req or "spec" in req or "architecture" in req:
                    return Phase.PLANNING
                elif "implement" in req or "feature" in req or "bugfix" in req:
                    return Phase.IMPLEMENTATION
                elif "debug" in req or "bug" in req or "error" in req:
                    return Phase.DEBUGGING
                elif "verify" in req or "test" in req or "complete" in req or "quality" in req:
                    return Phase.VERIFICATION
                elif "skill" in req or "manage" in req or "install" in req:
                    return Phase.MANAGEMENT
                elif "domain" in req or "product" in req or "behavioral" in req:
                    return Phase.DOMAIN
                elif "generate" in req or "image" in req or "pdf" in req or "render" in req:
                    return Phase.GENERATION
        
        return Phase.IMPLEMENTATION
    
    def recommend_skills_by_phase(self, phase: Phase, limit: int = 5) -> List[SkillRecommendation]:
        context_aware = self.detection_rules.get("context_aware", {})
        phase_skills = context_aware.get(phase.value, [])
        
        recommendations = []
        
        for skill_name in phase_skills:
            if skill_name not in self.skills:
                continue
            
            skill = self.skills[skill_name]
            context = skill.get("context", {})
            priority = context.get("priority", 5)
            required_for = context.get("required_for", [])
            
            confidence = 1.0 - (priority / 10.0)
            reason = f"Phase {phase.value} requires skills for: {', '.join(required_for)}"
            
            recommendations.append(SkillRecommendation(
                skill_name=skill_name,
                priority=priority,
                required_for=required_for,
                confidence=confidence,
                reason=reason
            ))
        
        recommendations.sort(key=lambda x: (x.priority, -x.confidence))
        
        return recommendations[:limit]
    
    def detect_skill_conflicts(self, skills: List[str]) -> List[ConflictInfo]:
        conflicts = []
        
        skill_phases = {}
        for skill_name in skills:
            if skill_name in self.skills:
                skill = self.skills[skill_name]
                context = skill.get("context", {})
                phase = context.get("trigger_phase", "implementation")
                priority = context.get("priority", 5)
                skill_phases[skill_name] = {"phase": phase, "priority": priority}
        
        phase_groups = {}
        for skill_name, info in skill_phases.items():
            phase = info["phase"]
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append((skill_name, info["priority"]))
        
        for phase, skill_list in phase_groups.items():
            if len(skill_list) > 1:
                high_priority_skills = [s for s, p in skill_list if p <= 2]
                if len(high_priority_skills) > 1:
                    conflicts.append(ConflictInfo(
                        conflict_type="high_priority_conflict",
                        skills=[s for s, p in high_priority_skills],
                        description=f"Multiple high-priority skills in {phase} phase",
                        resolution=f"Choose one skill from: {', '.join([s for s, p in high_priority_skills])}"
                    ))
        
        for skill_name, info in skill_phases.items():
            skill = self.skills[skill_name]
            context = skill.get("context", {})
            required_for = context.get("required_for", [])
            
            for req in required_for:
                for other_skill_name in skills:
                    if other_skill_name == skill_name:
                        continue
                    
                    other_skill = self.skills[other_skill_name]
                    other_context = other_skill.get("context", {})
                    other_required_for = other_context.get("required_for", [])
                    
                    if req in other_required_for:
                        conflicts.append(ConflictInfo(
                            conflict_type="dependency_conflict",
                            skills=[skill_name, other_skill_name],
                            description=f"Both skills require {req}",
                            resolution=f"Consider using one skill that covers {req} or use them sequentially"
                        ))
        
        incompatible_phases = [
            (Phase.IDEATION, Phase.VERIFICATION),
            (Phase.VERIFICATION, Phase.IDEATION),
            (Phase.DEBUGGING, Phase.IDEATION),
            (Phase.IDEATION, Phase.DEBUGGING),
            (Phase.GENERATION, Phase.DEBUGGING),
            (Phase.DEBUGGING, Phase.GENERATION)
        ]
        
        for skill1_name, skill2_name in [(s1, s2) for i, s1 in enumerate(skills) for s2 in skills[i+1:]]:
            if skill1_name not in skill_phases or skill2_name not in skill_phases:
                continue
            
            phase1 = skill_phases[skill1_name]["phase"]
            phase2 = skill_phases[skill2_name]["phase"]
            
            try:
                phase1_enum = Phase(phase1)
                phase2_enum = Phase(phase2)
            except ValueError:
                continue
            
            for phase_a, phase_b in incompatible_phases:
                if (phase1_enum == phase_a and phase2_enum == phase_b):
                    conflicts.append(ConflictInfo(
                        conflict_type="phase_conflict",
                        skills=[skill1_name, skill2_name],
                        description=f"Skills from incompatible phases: {phase1} and {phase2}",
                        resolution=f"Use skills in sequence: {phase1} first, then {phase2}"
                    ))
        
        return conflicts
    
    def route(self, user_input: str) -> Dict:
        context_info = self.detect_context_from_user_input(user_input)
        
        recommendations = self.recommend_skills_by_phase(context_info.phase)
        
        skill_names = [r.skill_name for r in recommendations]
        conflicts = self.detect_skill_conflicts(skill_names)
        
        return {
            "user_input": user_input,
            "detected_phase": context_info.phase.value,
            "confidence": context_info.confidence,
            "keywords": context_info.keywords,
            "detected_intents": context_info.detected_intents,
            "recommendations": [
                {
                    "skill_name": r.skill_name,
                    "priority": r.priority,
                    "required_for": r.required_for,
                    "confidence": r.confidence,
                    "reason": r.reason
                }
                for r in recommendations
            ],
            "conflicts": [
                {
                    "conflict_type": c.conflict_type,
                    "skills": c.skills,
                    "description": c.description,
                    "resolution": c.resolution
                }
                for c in conflicts
            ]
        }
    
    def _exact_match(self, user_input: str) -> Optional[Dict]:
        exact_matches = self.detection_rules.get("exact_match", {})
        user_input_lower = user_input.lower().strip()
        
        for trigger, skill_name in exact_matches.items():
            if user_input_lower == trigger.lower():
                if skill_name in self.skills:
                    skill = self.skills[skill_name]
                    context = skill.get("context", {})
                    return {
                        "skill_name": skill_name,
                        "matched_type": "exact_match",
                        "priority": 1,
                        "confidence": 1.0,
                        "trigger": trigger
                    }
        
        return None
    
    def _partial_match(self, user_input: str) -> List[Dict]:
        partial_matches = self.detection_rules.get("partial_match", {})
        user_input_lower = user_input.lower()
        candidates = []
        
        for keyword, skill_names in partial_matches.items():
            if keyword.lower() in user_input_lower:
                if isinstance(skill_names, str):
                    skill_names = [skill_names]
                
                for skill_name in skill_names:
                    if skill_name in self.skills:
                        skill = self.skills[skill_name]
                        keywords = skill.get("keywords", [])
                        
                        keyword_weight = 0
                        for kw in keywords:
                            if kw.lower() in user_input_lower:
                                keyword_weight += 1
                        
                        if keyword_weight > 0:
                            context = skill.get("context", {})
                            priority = context.get("priority", 5)
                            match_score = keyword_weight / len(keywords) if keywords else 0.5
                            confidence = min(0.9, match_score)
                            calculated_priority = 10 - int(confidence * 10) + 2
                            
                            candidates.append({
                                "skill_name": skill_name,
                                "matched_type": "partial_match",
                                "priority": min(priority, calculated_priority),
                                "confidence": confidence,
                                "keyword": keyword,
                                "match_score": match_score
                            })
        
        candidates.sort(key=lambda x: (x["priority"], -x["confidence"]))
        return candidates
    
    def _resolve_conflicts(self, candidates: List[Dict]) -> Tuple[Optional[Dict], List[ConflictInfo], str]:
        if not candidates:
            return None, [], "no_candidates"
        
        if len(candidates) == 1:
            return candidates[0], [], "single_candidate"
        
        conflicts = self.detect_skill_conflicts([c["skill_name"] for c in candidates])
        
        exact_matches = [c for c in candidates if c["matched_type"] == "exact_match"]
        if exact_matches:
            exact_matches.sort(key=lambda x: x["priority"])
            return exact_matches[0], conflicts, "exact_match_priority"
        
        partial_matches = [c for c in candidates if c["matched_type"] == "partial_match"]
        context_matches = [c for c in candidates if c["matched_type"] == "context_aware"]
        
        if partial_matches and context_matches:
            return partial_matches[0], conflicts, "partial_over_context"
        
        if partial_matches:
            partial_matches.sort(key=lambda x: (-x["confidence"], x["priority"]))
            return partial_matches[0], conflicts, "highest_confidence"
        
        candidates.sort(key=lambda x: (-x["confidence"], x["priority"]))
        return candidates[0], conflicts, "highest_confidence_fallback"
    
    def route_with_priority(self, user_input: str) -> RoutingDecision:
        timestamp = datetime.now().isoformat()
        
        exact_match = self._exact_match(user_input)
        if exact_match:
            return RoutingDecision(
                user_input=user_input,
                matched_type="exact_match",
                candidates=[exact_match],
                selected_skill=exact_match["skill_name"],
                priority=exact_match["priority"],
                confidence=exact_match["confidence"],
                conflicts=[],
                resolution_strategy="exact_match",
                timestamp=timestamp,
                feedback_history=[]
            )
        
        partial_matches = self._partial_match(user_input)
        
        if not partial_matches:
            context_info = self.detect_context_from_user_input(user_input)
            recommendations = self.recommend_skills_by_phase(context_info.phase)
            
            if recommendations:
                candidates = [
                    {
                        "skill_name": r.skill_name,
                        "matched_type": "context_aware",
                        "priority": r.priority,
                        "confidence": r.confidence,
                        "reason": r.reason
                    }
                    for r in recommendations
                ]
            else:
                candidates = []
        else:
            candidates = partial_matches
        
        if candidates:
            selected, conflicts, strategy = self._resolve_conflicts(candidates)
            
            return RoutingDecision(
                user_input=user_input,
                matched_type=selected["matched_type"] if selected else "no_match",
                candidates=candidates,
                selected_skill=selected["skill_name"] if selected else None,
                priority=selected["priority"] if selected else 10,
                confidence=selected["confidence"] if selected else 0.0,
                conflicts=conflicts,
                resolution_strategy=strategy,
                timestamp=timestamp,
                feedback_history=[]
            )
        else:
            return RoutingDecision(
                user_input=user_input,
                matched_type="no_match",
                candidates=[],
                selected_skill=None,
                priority=10,
                confidence=0.0,
                conflicts=[],
                resolution_strategy="default_route",
                timestamp=timestamp,
                feedback_history=[]
            )
    
    def multi_stage_route(self, user_input: str) -> Dict:
        timestamp = datetime.now().isoformat()
        
        stage1_result = self.route_with_priority(user_input)
        
        if stage1_result.selected_skill:
            skill = self.skills.get(stage1_result.selected_skill, {})
            context = skill.get("context", {})
            trigger_phase = context.get("trigger_phase", "implementation")
            
            phase_transitions = {
                "ideation": ["planning", "implementation"],
                "planning": ["implementation", "debugging"],
                "implementation": ["debugging", "verification"],
                "debugging": ["verification", "implementation"],
                "verification": ["implementation", "planning"],
                "management": ["implementation", "planning"],
                "domain": ["ideation", "planning"],
                "generation": ["verification", "implementation"]
            }
            
            next_phases = phase_transitions.get(trigger_phase, [])
            
            suggested_next_skills = []
            for next_phase in next_phases:
                phase_recommendations = self.recommend_skills_by_phase(Phase(next_phase), limit=2)
                for rec in phase_recommendations:
                    if rec.skill_name != stage1_result.selected_skill:
                        suggested_next_skills.append({
                            "skill_name": rec.skill_name,
                            "phase": next_phase,
                            "priority": rec.priority,
                            "confidence": rec.confidence,
                            "reason": f"Suggested next step after {trigger_phase}"
                        })
            
            return {
                "current_stage": {
                    "stage": 1,
                    "user_input": user_input,
                    "decision": {
                        "selected_skill": stage1_result.selected_skill,
                        "matched_type": stage1_result.matched_type,
                        "priority": stage1_result.priority,
                        "confidence": stage1_result.confidence,
                        "resolution_strategy": stage1_result.resolution_strategy
                    },
                    "phase": trigger_phase
                },
                "next_stages": {
                    "suggested_skills": suggested_next_skills[:3],
                    "phase_transitions": next_phases
                },
                "full_path": [stage1_result.selected_skill] if stage1_result.selected_skill else [],
                "timestamp": timestamp
            }
        else:
            return {
                "current_stage": {
                    "stage": 1,
                    "user_input": user_input,
                    "decision": {
                        "selected_skill": None,
                        "matched_type": "no_match",
                        "priority": 10,
                        "confidence": 0.0,
                        "resolution_strategy": "default_route"
                    },
                    "phase": "unknown"
                },
                "next_stages": {
                    "suggested_skills": [],
                    "phase_transitions": []
                },
                "full_path": [],
                "timestamp": timestamp
            }
    
    def route_with_feedback(self, user_input: str, feedback: Optional[Dict] = None) -> RoutingDecision:
        timestamp = datetime.now().isoformat()
        
        feedback_history = []
        if feedback:
            feedback_history = feedback.get("history", [])
            
            previous_skill = feedback.get("previous_skill")
            user_satisfaction = feedback.get("satisfaction", "neutral")
            alternative_suggestion = feedback.get("alternative_suggestion")
            
            if user_satisfaction == "low" and previous_skill:
                if previous_skill in self.skills:
                    skill = self.skills[previous_skill]
                    context = skill.get("context", {})
                    trigger_phase = context.get("trigger_phase", "implementation")
                    
                    phase_skills = self.recommend_skills_by_phase(Phase(trigger_phase), limit=5)
                    
                    alternative_candidates = [
                        {
                            "skill_name": r.skill_name,
                            "matched_type": "context_aware",
                            "priority": r.priority + 1,
                            "confidence": r.confidence * 0.9,
                            "reason": f"Alternative to {previous_skill} based on feedback"
                        }
                        for r in phase_skills
                        if r.skill_name != previous_skill
                    ]
                    
                    if alternative_suggestion and alternative_suggestion in self.skills:
                        alt_skill = self.skills[alternative_suggestion]
                        alt_context = alt_skill.get("context", {})
                        alternative_candidates.insert(0, {
                            "skill_name": alternative_suggestion,
                            "matched_type": "user_suggested",
                            "priority": alt_context.get("priority", 5),
                            "confidence": 0.95,
                            "reason": "User suggested alternative"
                        })
                    
                    if alternative_candidates:
                        selected, conflicts, strategy = self._resolve_conflicts(alternative_candidates)
                        
                        feedback_history.append({
                            "timestamp": timestamp,
                            "previous_skill": previous_skill,
                            "satisfaction": user_satisfaction,
                            "alternative_suggestion": alternative_suggestion,
                            "new_selection": selected["skill_name"] if selected else None
                        })
                        
                        return RoutingDecision(
                            user_input=user_input,
                            matched_type=selected["matched_type"] if selected else "no_match",
                            candidates=alternative_candidates,
                            selected_skill=selected["skill_name"] if selected else None,
                            priority=selected["priority"] if selected else 10,
                            confidence=selected["confidence"] if selected else 0.0,
                            conflicts=conflicts,
                            resolution_strategy=strategy,
                            timestamp=timestamp,
                            feedback_history=feedback_history
                        )
        
        result = self.route_with_priority(user_input)
        result.feedback_history = feedback_history
        return result


def main():
    import sys
    
    router = ContextAwareRouter()
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        print("Context-Aware Skill Router")
        print("=" * 50)
        print("Enter your input (or 'quit' to exit):")
        
        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            result = router.route(user_input)
            print_result(result)
        
        return
    
    result = router.route(user_input)
    print_result(result)


def print_result(result: Dict):
    print("\n" + "=" * 60)
    print(f"Detected Phase: {result['detected_phase'].upper()}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Keywords: {', '.join(result['keywords'])}")
    print(f"Detected Intents: {', '.join(result['detected_intents'])}")
    
    print("\n" + "-" * 60)
    print("Recommended Skills:")
    print("-" * 60)
    
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. {rec['skill_name']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Confidence: {rec['confidence']:.2f}")
        print(f"   Required For: {', '.join(rec['required_for'])}")
        print(f"   Reason: {rec['reason']}")
    
    if result['conflicts']:
        print("\n" + "-" * 60)
        print("Conflicts Detected:")
        print("-" * 60)
        
        for i, conflict in enumerate(result['conflicts'], 1):
            print(f"\n{i}. {conflict['conflict_type']}")
            print(f"   Skills: {', '.join(conflict['skills'])}")
            print(f"   Description: {conflict['description']}")
            print(f"   Resolution: {conflict['resolution']}")
    else:
        print("\n" + "-" * 60)
        print("No conflicts detected")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
