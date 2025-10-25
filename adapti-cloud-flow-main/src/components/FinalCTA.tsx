import { Button } from "@/components/ui/button";
import { ArrowRight, Github } from "lucide-react";

const FinalCTA = () => {
  return (
    <section className="py-24 bg-gradient-to-br from-teal/10 via-primary/5 to-violet/10 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-violet/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-teal/20 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-foreground">
            Deploy ATOM in Your Environment
            <br />
            <span className="bg-gradient-to-r from-teal via-primary to-violet bg-clip-text text-transparent">
              in Minutes
            </span>
          </h2>

          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
            Join AI teams building the future with self-adapting infrastructure. Open source, production-ready, and built for scale.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button 
              size="lg" 
              className="group bg-gradient-to-r from-teal to-violet hover:opacity-90 transition-all text-lg px-8 py-6 shadow-xl"
            >
              Start Building Now
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            
            <Button 
              size="lg" 
              variant="outline" 
              className="text-lg px-8 py-6 border-2 hover:border-primary hover:bg-secondary transition-all"
            >
              <Github className="mr-2 w-5 h-5" />
              View on GitHub
            </Button>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              <span>Deploy in 10 minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              <span>Zero vendor lock-in</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              <span>Production-ready</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;
