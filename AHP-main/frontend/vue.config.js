const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/save-survey': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/process-excel': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/save-survey-results': { 
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/survey-results': { 
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/survey-results/calculate': { 
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/survey-results/*/calculate': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      'api/login': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      'api/surveys/*': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    },
  },
});
