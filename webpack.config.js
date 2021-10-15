const path = require('path');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const config = {
  entry: path.resolve(__dirname, 'src/index'),
  output: {
    path: path.resolve(__dirname, 'app/public'),
    filename: "main.js"
  },
  resolve: {
    enforceExtension: false,
    extensions: [".jsx", ".js"],
    modules: ["node_modules"],
    alias: {
      '../../theme.config$': path.join(__dirname, 'semantic/theme.config')
    }
  },
  module: {
    rules: [{
        test: /\.jsx$/,
        use: ['babel-loader'],
        exclude: /node_modules/,
      },
      {
        test: /\.less$/,
        use: [{
          loader: "style-loader"
        }, {
          loader: "css-loader"
        }, {
          loader: "less-loader",
          options: {
            lessOptions: {
              math: "always"
            }
          }
        }],
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      {
        test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/],
        generator: {
          filename: 'images/[hash][ext][query]'
        },
        type: 'asset/inline'
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        generator: {
          filename: 'fonts/[hash][ext][query]'
        },
        type: 'asset/resource'
      }
    ]
  },
  plugins: [
    new webpack.EnvironmentPlugin(['NODE_ENV']),
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'src/assets/templates/index.template.ejs'),
      inject: 'body',
      filename: 'index.html'
    }),
    new ESLintPlugin({
      extensions: 'jsx',
    }),
  ],
  performance: {
    hints: false,
  },
  devServer: {
    proxy: {
      '/profile/**': {
        target: 'http://localhost:5000',
      },
      '/heatmap/**': {
        target: 'http://localhost:5000',
      },
      '/flamegraph/**': {
        target: 'http://localhost:5000',
      },
      '/differential/**': {
        target: 'http://localhost:5000',
      },
      '/elided/**': {
        target: 'http://localhost:5000',
      },
    },
  },
}

module.exports = (env, argv) => {
  if (argv.mode === 'development') {
    config.devtool = 'source-map';
  }

  return config;
};
