import autoprefixer from 'autoprefixer';
import webpack from 'webpack';
import BundleTracker from 'webpack-bundle-tracker';
import path from 'path';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import { fileURLToPath } from 'url';
import baseConfig from './webpack.base.config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const nodeModulesDir = path.resolve(__dirname, 'node_modules');

baseConfig.mode = 'production';
baseConfig.devtool = 'source-map';

baseConfig.entry = ['whatwg-fetch', './frontend/js/index.tsx'];

baseConfig.optimization = {
    splitChunks: {
        chunks: 'all',
        name: 'vendors~main',
    },
};

baseConfig.output = {
    path: path.resolve('./backend/js-build/webpack_bundles'),
    publicPath: '/static/',
    filename: '[name].js',
};

baseConfig.module.rules.push(
    {
        test: /\.tsx?$/,
        exclude: [nodeModulesDir],
        use: 'ts-loader',
    },
    {
        test: /\.(woff(2)?|eot|ttf)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
            {
                loader: 'file-loader',
                options: { name: 'fonts/[name].[ext]' },
            },
        ],
    }
);

baseConfig.plugins = [
    new webpack.DefinePlugin({
        // removes React warnings
        'process.env': {
            NODE_ENV: JSON.stringify('production'),
        },
    }),
    new MiniCssExtractPlugin({ filename: '[name]-[hash].css' }),
    new BundleTracker({
        filename: '../../webpack-stats.json',
    }),
    new webpack.LoaderOptionsPlugin({
        options: {
            context: __dirname,
            postcss: [autoprefixer],
        },
    }),
];

export default baseConfig;
