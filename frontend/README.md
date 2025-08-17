# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## データベースER図

このアプリケーションで使用するデータベースのER図は以下の通りです：

```mermaid
erDiagram
    stocks {
        INTEGER id
        TEXT symbol
        TEXT code
        TEXT name
        TEXT market_category
        TEXT industry_code_33
        TEXT industry_name_33
        TEXT industry_code_17
        TEXT industry_name_17
        TEXT scale_code
        TEXT scale_name
        TIMESTAMP last_fetched
        TIMESTAMP created_at
    }
    
    stock_prices {
        INTEGER id
        TEXT symbol
        TIMESTAMP date
        REAL open
        REAL high
        REAL low
        REAL close
        INTEGER volume
        TIMESTAMP created_at
    }
    
    technical_indicators {
        TEXT symbol
        TIMESTAMP date
        BOOLEAN golden_cross
        BOOLEAN dead_cross
        NUMERIC rsi
        NUMERIC macd
        NUMERIC signal_line
        TIMESTAMP created_at
    }
    
    recommendation_sessions {
        INTEGER session_id
        TIMESTAMP generated_at
        NUMERIC principal
        TEXT risk_tolerance
        TEXT strategy
        TEXT[] symbols
        TEXT technical_filter
        INTEGER prompt_id
    }
    
    recommendation_results {
        INTEGER id
        INTEGER session_id
        TEXT symbol
        TEXT name
        TEXT allocation
        NUMERIC confidence
        TEXT reason
    }
    
    prompt_templates {
        INTEGER id
        TEXT name
        TEXT agent_type
        TEXT system_role
        TEXT user_template
        TEXT output_format
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    stock_prices }|--|| stocks : "fk_stock_prices_stocks"
    technical_indicators }|--|| stocks : "FOREIGN KEY (symbol)"
    recommendation_results }|--|| stocks : "FOREIGN KEY (symbol)"
    recommendation_results }|--|| recommendation_sessions : "FOREIGN KEY (session_id)"
    recommendation_sessions }|--|| prompt_templates : "FOREIGN KEY (prompt_id)"
```

詳細なスキーマ定義は[backend/docs/ER.md](../backend/docs/ER.md)を参照してください。

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
