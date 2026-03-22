import React, { useState } from 'react';
import { Leaf, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ImageUpload from './components/ImageUpload';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResults(null);
    setError(null);
  };

  const clearImage = () => {
    setSelectedImage(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setResults(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      const response = await fetch('https://cropdoc-backend-production.up.railway.app/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis failed. Please try again.');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 transition-colors duration-300">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-emerald-500 rounded-lg text-white">
                <Leaf className="w-6 h-6" />
              </div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300">
                CropDoc
              </h1>
            </div>
            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">
              AI Crop Disease Detector
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Upload & Preview */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-sm border border-slate-200/50 dark:border-slate-800/50 relative overflow-hidden">
              {/* Decorative gradient blob */}
              <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
              
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                1. Upload Image
              </h2>
              
              <ImageUpload 
                onImageSelect={handleImageSelect} 
                previewUrl={previewUrl}
                onClear={clearImage}
                isLoading={isLoading}
              />

              <AnimatePresence>
                {selectedImage && !results && typeof previewUrl === 'string' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-6 flex flex-col items-center"
                  >
                    <button
                      onClick={handleAnalyze}
                      disabled={isLoading}
                      className="w-full relative group overflow-hidden rounded-2xl p-[1px]"
                    >
                      <span className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl opacity-70 group-hover:opacity-100 transition-opacity duration-300" />
                      <div className="relative bg-white dark:bg-slate-900 px-8 py-4 rounded-[15px] flex items-center justify-center gap-2 transition-all duration-300 group-hover:bg-opacity-0">
                        {isLoading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin text-emerald-600 group-hover:text-white" />
                            <span className="font-semibold text-emerald-600 group-hover:text-white">Analyzing...</span>
                          </>
                        ) : (
                          <span className="font-semibold text-emerald-600 group-hover:text-white group-hover:drop-shadow-md">
                            Run AI Analysis
                          </span>
                        )}
                      </div>
                    </button>
                    
                    {error && (
                      <div className="mt-4 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 flex items-start gap-3 text-sm w-full">
                        <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                        <p>{error}</p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-7">
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-sm border border-slate-200/50 dark:border-slate-800/50 h-full min-h-[500px] flex flex-col relative overflow-hidden lg:ml-4">
               {/* Decorative gradient blob */}
               <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-teal-500/5 rounded-full blur-3xl pointer-events-none" />
               
              <h2 className="text-lg font-semibold mb-6 flex items-center gap-2 relative z-10">
                2. Analysis Results
              </h2>
              
              <div className="flex-1 relative z-10">
                <ResultsPanel results={results} isLoading={isLoading} />
              </div>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}

export default App;
