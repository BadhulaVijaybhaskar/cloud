import { AlertCircle, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/card";

const ProblemSolution = () => {
  return (
    <section className="py-24 bg-gradient-to-b from-secondary to-background">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Problem */}
          <Card className="p-8 border-2 border-destructive/20 bg-gradient-to-br from-background to-destructive/5 hover:shadow-lg transition-all">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-destructive/10 rounded-lg">
                <AlertCircle className="w-8 h-8 text-destructive" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-2">The Problem</h3>
                <p className="text-muted-foreground">Traditional infrastructure challenges</p>
              </div>
            </div>
            <ul className="space-y-3 text-foreground/80">
              <li className="flex items-start gap-2">
                <span className="text-destructive mt-1">•</span>
                <span>AI infrastructure is complex, costly, and brittle</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-destructive mt-1">•</span>
                <span>Manual DevOps setup takes weeks of engineering time</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-destructive mt-1">•</span>
                <span>Scaling requires constant monitoring and intervention</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-destructive mt-1">•</span>
                <span>Security and observability are afterthoughts</span>
              </li>
            </ul>
          </Card>

          {/* Solution */}
          <Card className="p-8 border-2 border-accent/20 bg-gradient-to-br from-background to-accent/5 hover:shadow-lg transition-all">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-accent/10 rounded-lg">
                <CheckCircle2 className="w-8 h-8 text-accent" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-2">The Solution</h3>
                <p className="text-muted-foreground">ATOM's adaptive approach</p>
              </div>
            </div>
            <ul className="space-y-3 text-foreground/80">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                <span>Automates topology management and resource allocation</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                <span>Deploy production-ready AI infrastructure in minutes</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                <span>Self-heals and scales intelligently without intervention</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                <span>Built-in security, observability, and compliance</span>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default ProblemSolution;
