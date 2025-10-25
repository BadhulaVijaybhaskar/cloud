import { Card } from "@/components/ui/card";
import { Workflow, Database, Shield, Activity, Cloud, Zap } from "lucide-react";

const modules = [
  {
    icon: Workflow,
    title: "LangGraph Orchestration",
    description: "Intelligent workflow automation for RAG, LLM, and agentic systems with built-in state management.",
    color: "from-teal to-teal/70",
  },
  {
    icon: Database,
    title: "Vector Engine",
    description: "High-performance embeddings and semantic search across Postgres, Milvus, and DuckDB.",
    color: "from-violet to-violet/70",
  },
  {
    icon: Shield,
    title: "Vault Security",
    description: "Dynamic secrets management with RBAC, signed containers, and zero-trust architecture.",
    color: "from-primary to-primary/70",
  },
  {
    icon: Activity,
    title: "Built-in Observability",
    description: "Prometheus metrics, Grafana dashboards, and Loki logging integrated out of the box.",
    color: "from-accent to-accent/70",
  },
  {
    icon: Cloud,
    title: "Multi-Engine Data Layer",
    description: "Unified interface across Postgres, S3, and multiple vector databases for flexibility.",
    color: "from-teal/80 to-primary/80",
  },
  {
    icon: Zap,
    title: "Adaptive Autoscaling",
    description: "Self-adjusting topology that scales compute, storage, and vector operations on demand.",
    color: "from-violet/80 to-accent/80",
  },
];

const CoreModules = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            Core Modules
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need for production AI infrastructure, unified under one autonomous control plane
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module, index) => (
            <Card 
              key={index}
              className="group p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 bg-gradient-to-br from-card to-secondary border-2 hover:border-primary/30"
            >
              <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${module.color} mb-4 group-hover:scale-110 transition-transform`}>
                <module.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-foreground">
                {module.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {module.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CoreModules;
