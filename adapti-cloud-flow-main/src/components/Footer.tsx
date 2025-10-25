import { Github, Twitter, Linkedin } from "lucide-react";
import atomLogo from "@/assets/atom-logo.png";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-secondary border-t border-border py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <img 
                src={atomLogo} 
                alt="ATOM Logo" 
                className="w-10 h-10 mix-blend-lighten dark:mix-blend-screen"
              />
              <h3 className="text-2xl font-bold bg-gradient-to-r from-teal to-violet bg-clip-text text-transparent">
                ATOM
              </h3>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              The Self-Adapting AI Cloud
            </p>
            <div className="flex gap-3">
              <a href="#" className="p-2 rounded-lg bg-background hover:bg-accent/10 transition-colors">
                <Github className="w-5 h-5 text-foreground" />
              </a>
              <a href="#" className="p-2 rounded-lg bg-background hover:bg-accent/10 transition-colors">
                <Twitter className="w-5 h-5 text-foreground" />
              </a>
              <a href="#" className="p-2 rounded-lg bg-background hover:bg-accent/10 transition-colors">
                <Linkedin className="w-5 h-5 text-foreground" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold text-foreground mb-3">Product</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Features</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Pricing</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Use Cases</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Roadmap</a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold text-foreground mb-3">Resources</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Documentation</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">GitHub</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Community</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Blog</a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold text-foreground mb-3">Company</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">About</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Contact</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Careers</a>
              </li>
              <li>
                <a href="#" className="text-muted-foreground hover:text-accent transition-colors">Privacy</a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-border pt-8 text-center text-sm text-muted-foreground">
          <p>© {currentYear} ATOM — The Self-Adapting AI Cloud. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
