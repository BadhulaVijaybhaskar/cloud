import { Card } from "@/components/ui/card";
import { MessageSquare, GitBranch, Cog } from "lucide-react";

const useCases = [
  {
    icon: MessageSquare,
    title: "RAG Pipelines",
    description: "Deploy retrieval-augmented generation systems with vector search, embeddings, and LLM orchestration in minutes.",
    metrics: ["Sub-100ms query latency", "Billion-scale vector search", "Multi-model support"],
  },
  {
    icon: GitBranch,
    title: "Data Workflows",
    description: "Build intelligent data pipelines with automatic scaling, transformation, and routing based on content and load.",
    metrics: ["Event-driven processing", "Auto-retry & healing", "Schema evolution"],
  },
  {
    icon: Cog,
    title: "Platform Automation",
    description: "Create self-managing infrastructure that adapts to usage patterns, optimizes costs, and maintains SLAs autonomously.",
    metrics: ["Cost optimization", "SLA compliance", "Zero-downtime updates"],
  },
];

const UseCases = () => {
  return (
    <section className="py-24 bg-gradient-to-b from-background to-secondary">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            Built for Modern AI Workloads
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From prototypes to production, ATOM scales with your AI ambitions
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {useCases.map((useCase, index) => (
            <Card 
              key={index}
              className="p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-2 bg-card border-2 hover:border-accent/30"
            >
              <div className="inline-flex p-4 rounded-xl bg-gradient-to-br from-teal/10 to-violet/10 mb-6">
                <useCase.icon className="w-8 h-8 text-primary" />
              </div>
              
              <h3 className="text-2xl font-semibold mb-3 text-foreground">
                {useCase.title}
              </h3>
              
              <p className="text-muted-foreground mb-6 leading-relaxed">
                {useCase.description}
              </p>

              <div className="space-y-2">
                {useCase.metrics.map((metric, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-foreground/70">
                    <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                    <span>{metric}</span>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default UseCases;
