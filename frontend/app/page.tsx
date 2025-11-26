'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Search,
  MessageSquare,
  Shield,
  Zap,
  GitBranch,
  CheckCircle,
  ArrowRight,
} from 'lucide-react';

export default function HomePage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-brand-50 via-white to-blue-50" />
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-brand-100/50 to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text content */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-brand-100 text-brand-700 text-sm font-medium mb-6">
                <Zap className="w-4 h-4 mr-2" />
                AI-Powered Claims Investigation
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
                From FNOL to{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-blue-600">
                  Investigation Plan
                </span>{' '}
                in Seconds
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-xl">
                ClaimInvestigator AI helps claims specialists transform raw First Notice of Loss 
                data into structured investigation plans, professional file notes, and comprehensive 
                question sets—powered by multi-model AI.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="/dashboard"
                  className="btn-primary btn-lg group"
                >
                  Start Investigating
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </a>
                <a
                  href="#features"
                  className="btn-secondary btn-lg"
                >
                  Learn More
                </a>
              </div>
              
              {/* Trust badges */}
              <div className="mt-10 flex items-center gap-6 text-sm text-gray-500">
                <div className="flex items-center">
                  <Shield className="w-5 h-5 text-green-600 mr-2" />
                  PII Auto-Redaction
                </div>
                <div className="flex items-center">
                  <GitBranch className="w-5 h-5 text-brand-600 mr-2" />
                  Multi-Model AI
                </div>
              </div>
            </motion.div>
            
            {/* Right: Feature preview */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <div className="card p-6 shadow-panel">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900">Claim Triage Results</h3>
                  <span className="badge-blue">Auto BI</span>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Claim Classified</p>
                      <p className="text-sm text-gray-500">92% confidence • Moderate complexity</p>
                    </div>
                  </div>
                  
                  <div className="border-t border-gray-100 pt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Immediate Tasks</p>
                    <ul className="space-y-2">
                      <li className="flex items-center gap-2 text-sm">
                        <span className="priority-high">High</span>
                        Contact claimant for recorded statement
                      </li>
                      <li className="flex items-center gap-2 text-sm">
                        <span className="priority-high">High</span>
                        Request police report
                      </li>
                      <li className="flex items-center gap-2 text-sm">
                        <span className="priority-medium">Med</span>
                        Verify policy coverage dates
                      </li>
                    </ul>
                  </div>
                  
                  <div className="border-t border-gray-100 pt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Red Flags Identified</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="badge-red">Late Reporting</span>
                      <span className="badge-yellow">Pre-existing Condition?</span>
                    </div>
                  </div>
                </div>
                
                {/* Model indicator */}
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
                  <span>Processed by Claude Sonnet 4</span>
                  <span>1.2s</span>
                </div>
              </div>
              
              {/* Floating badges */}
              <div className="absolute -top-4 -right-4 card px-3 py-2 shadow-lg">
                <span className="text-sm font-medium text-green-600">✓ PII Redacted</span>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Claims Investigation
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Streamline your workflow with AI-powered tools designed specifically for 
              insurance claims professionals.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Claim Triage & Checklist
              </h3>
              <p className="text-gray-600">
                Automatically classify claim types and generate prioritized investigation 
                checklists with deadlines and next steps.
              </p>
            </motion.div>

            {/* Feature 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center mb-4">
                <MessageSquare className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Investigation Questions
              </h3>
              <p className="text-gray-600">
                Generate tailored interview questions for claimants, witnesses, and insureds 
                covering liability, damages, and coverage.
              </p>
            </motion.div>

            {/* Feature 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center mb-4">
                <Search className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Coverage Issue Spotter
              </h3>
              <p className="text-gray-600">
                Identify potential coverage issues, liability concerns, and red flags 
                with clear action items for resolution.
              </p>
            </motion.div>

            {/* Feature 4 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                File Note Generator
              </h3>
              <p className="text-gray-600">
                Create professional claim notes and diary entries that document activities, 
                findings, and action plans.
              </p>
            </motion.div>

            {/* Feature 5 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center mb-4">
                <GitBranch className="w-6 h-6 text-brand-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Multi-Model AI Routing
              </h3>
              <p className="text-gray-600">
                Intelligently routes tasks to Claude, GPT-4, Gemini, or Azure OpenAI 
                based on task type for optimal results.
              </p>
            </motion.div>

            {/* Feature 6 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="card p-6"
            >
              <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Privacy-First Design
              </h3>
              <p className="text-gray-600">
                Automatic PII redaction ensures sensitive claimant and policyholder 
                data never leaves your environment unprotected.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-brand-600 to-brand-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Claims Workflow?
            </h2>
            <p className="text-xl text-brand-100 mb-8">
              Start investigating claims more efficiently with AI-powered assistance.
            </p>
            <a
              href="/dashboard"
              className="inline-flex items-center px-8 py-4 bg-white text-brand-700 font-semibold rounded-xl hover:bg-brand-50 transition-colors shadow-lg group"
            >
              Open Dashboard
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </a>
          </motion.div>
        </div>
      </section>
    </div>
  );
}