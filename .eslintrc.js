module.exports = {
    // So parent files don't get applied
    root: true,
    env: {
      es6: true,
      browser: true,
      node: true,
    },
    extends: [
      'eslint:recommended',
      'plugin:react/recommended'
    ],
    parser: 'babel-eslint',
    parserOptions: {
      ecmaVersion: 7,
      sourceType: 'module',
      ecmaFeatures: {
        jsx: true,
      }
    },
    plugins: [
      'babel',
      'react',
      'mocha'
    ],
    rules: {
      'no-console': ['off'] 
    },
    settings: {
      react: {
        version: "16.6",
      },
    },
};
