import React, { useState, useCallback } from 'react';
import { Settings, Save, RotateCcw, Info, Zap, Clock, Database } from 'lucide-react';

interface PerformanceSettings {
  debounceDelay: number;
  throttleDelay: number;
  cacheSize: number;
  cacheExpiration: number;
  enableMetrics: boolean;
  enableCache: boolean;
  autoOptimize: boolean;
}

interface AdvancedSettingsProps {
  className?: string;
  onSettingsChange?: (settings: PerformanceSettings) => void;
  currentSettings?: Partial<PerformanceSettings>;
}

const DEFAULT_SETTINGS: PerformanceSettings = {
  debounceDelay: 500,
  throttleDelay: 100,
  cacheSize: 50,
  cacheExpiration: 300000, // 5 minutos
  enableMetrics: true,
  enableCache: true,
  autoOptimize: false,
};

/**
 * Componente para configurações avançadas de performance
 */
export const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({
  className = '',
  onSettingsChange,
  currentSettings = {},
}) => {
  const [settings, setSettings] = useState<PerformanceSettings>({
    ...DEFAULT_SETTINGS,
    ...currentSettings,
  });
  
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  
  const handleSettingChange = useCallback(<K extends keyof PerformanceSettings>(
    key: K,
    value: PerformanceSettings[K]
  ) => {
    setSettings(prev => {
      const newSettings = { ...prev, [key]: value };
      setHasChanges(JSON.stringify(newSettings) !== JSON.stringify({ ...DEFAULT_SETTINGS, ...currentSettings }));
      return newSettings;
    });
  }, [currentSettings]);
  
  const handleSave = useCallback(() => {
    onSettingsChange?.(settings);
    setHasChanges(false);
  }, [settings, onSettingsChange]);
  
  const handleReset = useCallback(() => {
    const resetSettings = { ...DEFAULT_SETTINGS, ...currentSettings };
    setSettings(resetSettings);
    setHasChanges(false);
  }, [currentSettings]);
  
  const getRecommendation = (key: keyof PerformanceSettings, value: any) => {
    switch (key) {
      case 'debounceDelay':
        if (value < 200) return { type: 'warning', text: 'Very low delay may cause excessive API calls' };
        if (value > 1000) return { type: 'info', text: 'High delay may feel sluggish to users' };
        return { type: 'success', text: 'Good balance between performance and responsiveness' };
      
      case 'throttleDelay':
        if (value < 50) return { type: 'warning', text: 'Too low may not provide throttling benefits' };
        if (value > 200) return { type: 'info', text: 'High delay may cause choppy interactions' };
        return { type: 'success', text: 'Optimal for smooth interactions' };
      
      case 'cacheSize':
        if (value < 20) return { type: 'warning', text: 'Small cache may reduce hit rate' };
        if (value > 100) return { type: 'info', text: 'Large cache uses more memory' };
        return { type: 'success', text: 'Good balance between memory and performance' };
      
      case 'cacheExpiration':
        const minutes = value / 60000;
        if (minutes < 2) return { type: 'warning', text: 'Short expiration may reduce cache benefits' };
        if (minutes > 15) return { type: 'info', text: 'Long expiration may serve stale data' };
        return { type: 'success', text: 'Good balance between freshness and performance' };
      
      default:
        return null;
    }
  };
  
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Advanced Settings</h3>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 transition-colors"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="p-4 space-y-6">
          {/* Performance Settings */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              Performance Tuning
            </h4>
            
            <div className="space-y-4">
              {/* Debounce Delay */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Debounce Delay (ms)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="100"
                    max="2000"
                    step="100"
                    value={settings.debounceDelay}
                    onChange={(e) => handleSettingChange('debounceDelay', parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="100"
                    max="2000"
                    value={settings.debounceDelay}
                    onChange={(e) => handleSettingChange('debounceDelay', parseInt(e.target.value))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                {(() => {
                  const rec = getRecommendation('debounceDelay', settings.debounceDelay);
                  return rec && (
                    <p className={`text-xs mt-1 ${
                      rec.type === 'success' ? 'text-green-600' :
                      rec.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                    }`}>
                      {rec.text}
                    </p>
                  );
                })()}
              </div>
              
              {/* Throttle Delay */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Throttle Delay (ms)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="25"
                    max="500"
                    step="25"
                    value={settings.throttleDelay}
                    onChange={(e) => handleSettingChange('throttleDelay', parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="25"
                    max="500"
                    value={settings.throttleDelay}
                    onChange={(e) => handleSettingChange('throttleDelay', parseInt(e.target.value))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                {(() => {
                  const rec = getRecommendation('throttleDelay', settings.throttleDelay);
                  return rec && (
                    <p className={`text-xs mt-1 ${
                      rec.type === 'success' ? 'text-green-600' :
                      rec.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                    }`}>
                      {rec.text}
                    </p>
                  );
                })()}
              </div>
            </div>
          </div>
          
          {/* Cache Settings */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-500" />
              Cache Configuration
            </h4>
            
            <div className="space-y-4">
              {/* Cache Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cache Size (entries)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="10"
                    max="200"
                    step="10"
                    value={settings.cacheSize}
                    onChange={(e) => handleSettingChange('cacheSize', parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="10"
                    max="200"
                    value={settings.cacheSize}
                    onChange={(e) => handleSettingChange('cacheSize', parseInt(e.target.value))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                {(() => {
                  const rec = getRecommendation('cacheSize', settings.cacheSize);
                  return rec && (
                    <p className={`text-xs mt-1 ${
                      rec.type === 'success' ? 'text-green-600' :
                      rec.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                    }`}>
                      {rec.text}
                    </p>
                  );
                })()}
              </div>
              
              {/* Cache Expiration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cache Expiration (minutes)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="1"
                    max="30"
                    step="1"
                    value={settings.cacheExpiration / 60000}
                    onChange={(e) => handleSettingChange('cacheExpiration', parseInt(e.target.value) * 60000)}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={settings.cacheExpiration / 60000}
                    onChange={(e) => handleSettingChange('cacheExpiration', parseInt(e.target.value) * 60000)}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
                {(() => {
                  const rec = getRecommendation('cacheExpiration', settings.cacheExpiration);
                  return rec && (
                    <p className={`text-xs mt-1 ${
                      rec.type === 'success' ? 'text-green-600' :
                      rec.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                    }`}>
                      {rec.text}
                    </p>
                  );
                })()}
              </div>
            </div>
          </div>
          
          {/* Feature Toggles */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4 text-green-500" />
              Feature Toggles
            </h4>
            
            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.enableMetrics}
                  onChange={(e) => handleSettingChange('enableMetrics', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Enable Performance Metrics</span>
              </label>
              
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.enableCache}
                  onChange={(e) => handleSettingChange('enableCache', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Enable Filter Caching</span>
              </label>
              
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.autoOptimize}
                  onChange={(e) => handleSettingChange('autoOptimize', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Auto-optimize Settings</span>
              </label>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-700 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset to Defaults
            </button>
            
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-colors ${
                hasChanges
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
          
          {/* Performance Tips */}
          <div className="p-3 bg-blue-50 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-2">💡 Performance Tips</h5>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Lower debounce delays improve responsiveness but increase API calls</li>
              <li>• Higher cache sizes improve hit rates but use more memory</li>
              <li>• Enable auto-optimize to automatically adjust settings based on usage</li>
              <li>• Monitor performance metrics to identify bottlenecks</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedSettings;