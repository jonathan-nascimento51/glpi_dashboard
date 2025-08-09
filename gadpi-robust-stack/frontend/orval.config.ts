export default {
  api: {
    input: process.env.OPENAPI_URL ?? 'http://localhost:8000/openapi.json',
    output: {
      mode: 'tags-split',
      target: 'src/api/generated',
      client: 'react-query',
      override: {
        mutator: { path: 'src/api/http.ts', name: 'customInstance' }
      }
    }
  }
}