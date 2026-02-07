import { useState, useEffect } from 'react';
import { Zap, ChevronRight, Layers, CheckCircle2, Loader2, AlertTriangle, X } from 'lucide-react';
import axios from 'axios';
import { cn } from '../App';

// ─── Types ──────────────────────────────────────────────────────────
interface Skill {
  skill_id: string;
  display_name: string;
  category: string;
  automation_level: string;
  approval_required: boolean;
  description: string;
  when_to_use: string[];
}

interface WorkflowStep {
  skill_id: string;
  action: string;
  order: number;
}

interface Workflow {
  workflow_id: string;
  display_name: string;
  description: string;
  trigger: string;
  steps: WorkflowStep[];
}

// ─── Category Colors ────────────────────────────────────────────────
const categoryColors: Record<string, string> = {
  code:        'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  design:      'bg-pink-500/10 text-pink-400 border-pink-500/30',
  deployment:  'bg-amber-500/10 text-amber-400 border-amber-500/30',
  marketing:   'bg-violet-500/10 text-violet-400 border-violet-500/30',
  operations:  'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  analytics:   'bg-blue-500/10 text-blue-400 border-blue-500/30',
  content:     'bg-rose-500/10 text-rose-400 border-rose-500/30',
  creative:    'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30',
};

const automationBadge: Record<string, string> = {
  full:        'bg-green-500/20 text-green-300',
  supervised:  'bg-yellow-500/20 text-yellow-300',
  human:       'bg-red-500/20 text-red-300',
};

// ─── Component ──────────────────────────────────────────────────────
interface SkillsDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SkillsDashboard({ isOpen, onClose }: SkillsDashboardProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'skills' | 'workflows'>('skills');
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    fetchData();
  }, [isOpen]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [skillsRes, workflowsRes] = await Promise.all([
        axios.get('http://localhost:8000/skills/list'),
        axios.get('http://localhost:8000/skills/workflows/list'),
      ]);
      setSkills(skillsRes.data);
      setWorkflows(workflowsRes.data);
    } catch {
      setError('Could not load skills. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // ── Skill Detail Drawer ──
  const SkillDetail = ({ skill }: { skill: Skill }) => (
    <div className="p-5 space-y-4 animate-in slide-in-from-right-4 duration-200">
      <button onClick={() => setSelectedSkill(null)} className="text-xs text-neutral-400 hover:text-white flex items-center gap-1">
        &larr; Back to all skills
      </button>
      <h3 className="text-lg font-bold text-white">{skill.display_name}</h3>
      <p className="text-sm text-neutral-300 leading-relaxed">{skill.description}</p>

      <div className="flex flex-wrap gap-2">
        <span className={cn('text-[10px] px-2 py-0.5 rounded-full border', categoryColors[skill.category] || 'bg-neutral-800 text-neutral-400 border-neutral-700')}>
          {skill.category}
        </span>
        <span className={cn('text-[10px] px-2 py-0.5 rounded-full', automationBadge[skill.automation_level] || 'bg-neutral-800 text-neutral-300')}>
          {skill.automation_level}
        </span>
        {skill.approval_required && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-300 flex items-center gap-1">
            <AlertTriangle size={10} /> Approval Required
          </span>
        )}
      </div>

      {skill.when_to_use.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">When to use</h4>
          <ul className="space-y-1">
            {skill.when_to_use.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-neutral-300">
                <ChevronRight size={14} className="mt-0.5 text-pink-400 shrink-0" /> {w}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  // ── Workflow Detail Drawer ──
  const WorkflowDetail = ({ workflow }: { workflow: Workflow }) => (
    <div className="p-5 space-y-4 animate-in slide-in-from-right-4 duration-200">
      <button onClick={() => setSelectedWorkflow(null)} className="text-xs text-neutral-400 hover:text-white flex items-center gap-1">
        &larr; Back to all workflows
      </button>
      <h3 className="text-lg font-bold text-white">{workflow.display_name}</h3>
      <p className="text-sm text-neutral-300 leading-relaxed">{workflow.description}</p>
      <p className="text-xs text-neutral-500">Trigger: <span className="text-neutral-300">{workflow.trigger}</span></p>

      <div>
        <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">Steps</h4>
        <div className="space-y-2">
          {workflow.steps.map((step) => (
            <div key={step.order} className="flex items-start gap-3 p-3 bg-neutral-800/50 rounded-lg border border-neutral-800">
              <span className="w-6 h-6 rounded-full bg-pink-600/20 text-pink-400 text-xs flex items-center justify-center font-bold shrink-0">
                {step.order}
              </span>
              <div>
                <span className="text-sm font-medium text-white">{step.action}</span>
                <span className="block text-[10px] text-neutral-500 mt-0.5">Skill: {step.skill_id}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl max-h-[85vh] bg-neutral-900 border border-neutral-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">

        {/* Header */}
        <div className="p-4 border-b border-neutral-800 flex items-center justify-between bg-neutral-800/50">
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-pink-400" />
            <h2 className="font-semibold text-white">Synthia Skills & Workflows</h2>
            <span className="text-[10px] bg-pink-600/20 text-pink-300 px-1.5 py-0.5 rounded">
              {skills.length} skills · {workflows.length} flows
            </span>
          </div>
          <button onClick={onClose} className="text-neutral-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-neutral-800">
          <button
            onClick={() => { setActiveTab('skills'); setSelectedSkill(null); setSelectedWorkflow(null); }}
            className={cn(
              'flex-1 px-4 py-2.5 text-sm font-medium transition-colors',
              activeTab === 'skills' ? 'text-pink-400 border-b-2 border-pink-500' : 'text-neutral-500 hover:text-neutral-300'
            )}
          >
            <Zap size={14} className="inline mr-1.5 -mt-0.5" /> Skills ({skills.length})
          </button>
          <button
            onClick={() => { setActiveTab('workflows'); setSelectedSkill(null); setSelectedWorkflow(null); }}
            className={cn(
              'flex-1 px-4 py-2.5 text-sm font-medium transition-colors',
              activeTab === 'workflows' ? 'text-pink-400 border-b-2 border-pink-500' : 'text-neutral-500 hover:text-neutral-300'
            )}
          >
            <Layers size={14} className="inline mr-1.5 -mt-0.5" /> Workflows ({workflows.length})
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 text-neutral-500">
              <Loader2 className="animate-spin mb-3" size={28} />
              <span className="text-sm">Loading skills engine...</span>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
              <AlertTriangle size={28} className="text-red-400 mb-3" />
              <p className="text-sm text-red-300 mb-3">{error}</p>
              <button onClick={fetchData} className="text-xs text-pink-400 hover:underline">Retry</button>
            </div>
          ) : activeTab === 'skills' ? (
            selectedSkill ? (
              <SkillDetail skill={selectedSkill} />
            ) : (
              <div className="p-4 grid gap-2">
                {skills.map((skill) => (
                  <button
                    key={skill.skill_id}
                    onClick={() => setSelectedSkill(skill)}
                    className="w-full text-left p-3 bg-neutral-800/40 hover:bg-neutral-800/80 rounded-xl border border-neutral-800 hover:border-neutral-700 transition-all group flex items-center justify-between"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-white truncate">{skill.display_name}</span>
                        <span className={cn('text-[10px] px-1.5 py-0.5 rounded-full border shrink-0', categoryColors[skill.category] || 'bg-neutral-800 text-neutral-400 border-neutral-700')}>
                          {skill.category}
                        </span>
                      </div>
                      <p className="text-xs text-neutral-500 truncate">{skill.description}</p>
                    </div>
                    <ChevronRight size={16} className="text-neutral-600 group-hover:text-pink-400 transition-colors shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            )
          ) : (
            selectedWorkflow ? (
              <WorkflowDetail workflow={selectedWorkflow} />
            ) : (
              <div className="p-4 grid gap-2">
                {workflows.map((wf) => (
                  <button
                    key={wf.workflow_id}
                    onClick={() => setSelectedWorkflow(wf)}
                    className="w-full text-left p-3 bg-neutral-800/40 hover:bg-neutral-800/80 rounded-xl border border-neutral-800 hover:border-neutral-700 transition-all group flex items-center justify-between"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-white truncate">{wf.display_name}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-neutral-700/50 text-neutral-400 shrink-0">
                          {wf.steps.length} steps
                        </span>
                      </div>
                      <p className="text-xs text-neutral-500 truncate">{wf.description}</p>
                    </div>
                    <ChevronRight size={16} className="text-neutral-600 group-hover:text-pink-400 transition-colors shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            )
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-neutral-800 bg-neutral-900 flex items-center justify-between text-[10px] text-neutral-600">
          <span>Synthia 4.2 Skills Engine</span>
          <span className="flex items-center gap-1">
            <CheckCircle2 size={10} className="text-green-500" /> All systems operational
          </span>
        </div>
      </div>
    </div>
  );
}
