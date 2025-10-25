import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import atomLogo from "@/assets/atom-logo.png";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-background via-background to-secondary">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet/20 rounded-full blur-3xl animate-float" style={{ animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-primary/10 rounded-full blur-3xl animate-glow" />
      </div>

      {/* Orbital atom visualization */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="relative w-[300px] h-[300px]">
          {/* Core */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-gradient-to-br from-teal to-violet rounded-full animate-glow shadow-[0_0_40px_rgba(59,130,246,0.5)]" />
          
          {/* Orbiting particles */}
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{ 
                animationDelay: `${i * 2}s`,
              }}
            >
              <div className="w-3 h-3 bg-accent rounded-full animate-orbit" />
            </div>
          ))}
        </div>
      </div>

      {/* Hero content */}
      <div className="relative z-10 container mx-auto px-4 text-center">
        <div className="flex items-center justify-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-accent animate-pulse" />
          <span className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Adaptive Topology Orchestration Module
          </span>
        </div>

        <div className="flex items-center justify-center gap-4 mb-6">
          <img 
            src={atomLogo} 
            alt="ATOM Logo" 
            className="w-16 h-16 md:w-20 md:h-20 lg:w-24 lg:h-24 mix-blend-lighten dark:mix-blend-screen"
          />
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold bg-gradient-to-r from-teal via-primary to-violet bg-clip-text text-transparent">
            ATOM
          </h1>
        </div>

        <p className="text-2xl md:text-3xl lg:text-4xl font-semibold mb-6 text-foreground">
          The Self-Adapting AI Cloud
        </p>

        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-12 leading-relaxed">
          Automate workflows, scale vectors, and deploy RAG pipelines with an intelligent, autonomous control plane.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button size="lg" className="group bg-gradient-to-r from-teal to-violet hover:opacity-90 transition-all text-lg px-8 py-6 shadow-lg hover:shadow-xl">
            Get Started
            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-2 hover:border-primary hover:bg-secondary transition-all">
            View Documentation
          </Button>
        </div>

        <div className="mt-16 text-sm text-muted-foreground">
          Trusted by AI teams processing 1M+ queries/day
        </div>
      </div>
    </section>
  );
};

export default Hero;
