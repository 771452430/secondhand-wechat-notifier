SECONDHAND_CONFIG = """site:
  api_base_url: "http://localhost:4000/api/v1"
  web_base_url: "http://localhost:3000"

wechat:
  group_name: "闲置小市场通知群"

sender:
  type: "macos-accessibility"

poll:
  enabled: true
  interval_seconds: 60

schedule:
  daily_digest_time: "09:00"
  timezone: "Asia/Shanghai"

storage:
  sqlite_path: "./notifier-state.sqlite3"

digest:
  combine_sources: true

sources:
  - name: "listings"
    label: "闲置"
    url: "/listings"
    method: "GET"
    query:
      page: 1
      pageSize: 3
      status: "ACTIVE"
    items_path: "items"
    id_field: "id"
    created_at_field: "createdAt"
    detail_url_template: "{web_base_url}/listings/{id}"
    fields:
      title: "title"
      price: "price"
      category: "category"
      location: "locationText"
      author: "author.displayName"
    message_template: |
      【新闲置】{title}
      价格：¥{price}
      地点：{location}
      发布人：{author}
      详情：{url}

  - name: "wanted_posts"
    label: "求购"
    url: "/wanted-posts"
    method: "GET"
    query:
      page: 1
      pageSize: 3
      status: "OPEN"
    items_path: "items"
    id_field: "id"
    created_at_field: "createdAt"
    detail_url_template: "{web_base_url}/wanted/{id}"
    fields:
      title: "title"
      budget_min: "budgetMin"
      budget_max: "budgetMax"
      category: "category"
      location: "locationText"
      author: "author.displayName"
    message_template: |
      【新求购】{title}
      预算：{budget_min}-{budget_max}
      地点：{location}
      发布人：{author}
      详情：{url}
"""
