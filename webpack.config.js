const path = require('path');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
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
        loaders: ['babel-loader'],
        exclude: /node_modules/,
      },
      {
        test: /\.less$/,
        use: [{
          loader: "style-loader"
        }, {
            loader: "css-loader"
        }, {
            loader: "less-loader"
        }],
      },
      {
        test: /\.css$/,
        loader: "style-loader!css-loader",
      },
      {
        test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/],
        loader: require.resolve('url-loader'),
        options: {
          limit: 10000,
          name: 'images/[name].[ext]',
        },
      },
      {
        test: [/\.eot$/, /\.ttf$/, /\.svg$/, /\.woff$/, /\.woff2$/],
        loader: require.resolve('file-loader'),
        options: {
          name: 'fonts/[name].[ext]',
        }
      },
      {
        test: /\.jsx$/,
        enforce: "pre",
        loader: "eslint-loader",
        exclude: /node_modules/,
      }
    ]
  },
  plugins: [
    new webpack.EnvironmentPlugin(['NODE_ENV']),
    new webpack.LoaderOptionsPlugin({
      options: {
        eslint: {
          configFile: '.eslintrc.js'
        }
      }
    }),
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'src/assets/templates/index.template.ejs'),
      inject: 'body',
      filename: 'index.html'
    })
  ],
  performance: {
    hints: false,
  },
}

