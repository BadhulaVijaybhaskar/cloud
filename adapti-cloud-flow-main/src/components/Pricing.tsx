import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Check } from "lucide-react";

const plans = [
  {
    name: "Open Source",
    price: "Free",
    description: "Perfect for development and testing",
    features: [
      "Full source code access",
      "Community support",
      "Self-hosted deployment",
      "Core modules included",
      "Regular updates",
    ],
    cta: "Get Started",
    variant: "outline" as const,
  },
  {
    name: "Managed Cloud",
    price: "$499",
    period: "/month",
    description: "Production-ready managed infrastructure",
    features: [
      "Everything in Open Source",
      "Managed hosting & updates",
      "24/7 monitoring & support",
      "SLA guarantees",
      "Advanced security features",
      "Custom integrations",
    ],
    cta: "Start Free Trial",
    variant: "default" as const,
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large-scale AI operations",
    features: [
      "Everything in Managed Cloud",
      "Dedicated infrastructure",
      "Custom SLA & support",
      "Training & onboarding",
      "Priority feature requests",
      "Architecture consultation",
    ],
    cta: "Contact Sales",
    variant: "outline" as const,
  },
];

const Pricing = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your needs. Scale as you grow.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card 
              key={index}
              className={`p-8 flex flex-col ${
                plan.highlighted 
                  ? 'border-2 border-primary shadow-xl relative' 
                  : 'border-2 hover:border-primary/30'
              } transition-all duration-300 hover:-translate-y-1`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-teal to-violet text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  {plan.name}
                </h3>
                <div className="mb-2">
                  <span className="text-4xl font-bold text-foreground">
                    {plan.price}
                  </span>
                  {plan.period && (
                    <span className="text-muted-foreground">{plan.period}</span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  {plan.description}
                </p>
              </div>

              <ul className="space-y-3 mb-8 flex-grow">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                    <span className="text-foreground/80">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button 
                variant={plan.variant}
                className={`w-full ${
                  plan.highlighted 
                    ? 'bg-gradient-to-r from-teal to-violet hover:opacity-90' 
                    : ''
                }`}
                size="lg"
              >
                {plan.cta}
              </Button>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-muted-foreground mb-4">
            All plans include access to core modules and regular updates
          </p>
          <p className="text-sm text-muted-foreground">
            Need help choosing? <span className="text-accent hover:underline cursor-pointer">Contact our team</span>
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
