import Hero from "@/components/Hero";
import ProblemSolution from "@/components/ProblemSolution";
import CoreModules from "@/components/CoreModules";
import UseCases from "@/components/UseCases";
import Pricing from "@/components/Pricing";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <main className="min-h-screen">
      <Hero />
      <ProblemSolution />
      <CoreModules />
      <UseCases />
      <Pricing />
      <FinalCTA />
      <Footer />
    </main>
  );
};

export default Index;
