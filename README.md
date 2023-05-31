# Simple coupon app with FastAPI, SQLModel and PostgresSQL

There are various paid services or products that are offered by a company or resellers to their customers.
In order to increase the shopping experience, customers must be given the opportunity to receive discounts with coupons.  
This is a simple and incomplete application that partially solves this issue.
It uses FastAPI and SQLModel to provide a proper web API to a PostgreSQL database.

There are five types of coupons:

-   percentage discount
-   fixed amount discount
-   some gift - it doesn't affect the price, just surprise me
-   queue bump - I'm with a baby :)
-   reduced fare for a reseller if she issues a sufficient number of coupons

The application should provide a REST API for:

-   creating coupons,
-   checking coupon validity,
-   activting/using coupon.

Because this is a super simple app skeleton, it doesn't use currency, just simple decimal numbers with limited precision.
A coupon can only be used by one customer and can only be used once.

## Schema

**Coupon**

-   id (primary key)
-   code (unique, str)
-   description (str)
-   created_at (datetime)
-   customer (optional, foreign key)
-   discount_type (enum)
-   discount (int)

**Customer**

-   id (primary key)
-   name (str)
-   created_at (datetime)

## Configuration

Configuration requires `python-dotenv` and is done with `pydantic.Settings`.
You have to access a PostgreSQL instance and configure it properly with an empty database for this project. You need to create a `.env` file with the appropriate DB connection parameters.
The default `username` and `password` are `couponConn`, and the DB name is `coupons`.

## CLI

A basic command line interface is built with Typer.  
Get help with this: `python -m coupon_cli.main --help`.

-   Clear connected db: `python -m coupon_cli.main clear-db`
-   Executes the demo fixture: `python -m coupon_cli.main demo-fixture`
