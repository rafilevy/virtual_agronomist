import autoprefixer from 'autoprefixer';
import webpack from 'webpack';
import BundleTracker from 'webpack-bundle-tracker';
import path from 'path';
import { fileURLToPath } from 'url';
import baseConfig from './webpack.base.config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const nodeModulesDir = path.resolve(__dirname, 'node_modules');

baseConfig.mode = 'development';

baseConfig.optimization = {
    splitChunks: {
        chunks: 'all',
        name: 'vendors~main',
    },
};

baseConfig.output = {
    path: path.resolve('./frontend/bundles/'),
    publicPath: 'http://localhost:3000/frontend/bundles/',
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
                loader: 'url-loader',
                options: { limit: 100000 },
            },
        ],
    }
);

baseConfig.plugins = [
    new webpack.EvalSourceMapDevToolPlugin({
        exclude: /node_modules/,
    }),
    new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
    new BundleTracker({
        filename: './webpack-stats.json',
    }),
    new webpack.LoaderOptionsPlugin({
        options: {
            context: __dirname,
            postcss: [autoprefixer],
        },
    }),
];

baseConfig.resolve.alias = {
    'react-dom': '@hot-loader/react-dom',
};

baseConfig.devServer = {
    contentBase: path.resolve(__dirname, "frontend", "dev"),
    hot: true
}

export default baseConfig;
