#!/usr/bin/env ruby
# frozen_string_literal: true

require "uri"

# Exercise the guide's actual rules with native Ruby matching. Mirror the pinned
# TopicEmbed.normalize_url before the EmbeddableHost path-plus-query lookup;
# no Discourse application, database or network is needed.
guide = File.read(ARGV.fetch(0, File.expand_path("../docs/discussions.md", __dir__)))
rules = guide.lines.grep(/\A\\A\//).map { |line| Regexp.new(line.strip) }
abort "Expected English and Czech article rules in the guide" unless rules.size == 2
hosts = %w[blog.vpsfree.org blog.vpsfree.cz]
rows = hosts.zip(rules).map { |host, rule| { host: host, rule: rule, category: 10 } }
checks = 0
check = lambda do |condition, message|
  abort message unless condition
  checks += 1
end
normalize = ->(url) { url.downcase.sub(%r{/\z}, "").sub(/\-+/, "-").strip }
lookup = lambda do |url, entries|
  uri = URI(url)
  host = uri.host
  host += ":#{uri.port}" unless [80, 443].include?(uri.port)
  path = uri.path + (uri.query ? "?#{uri.query}" : "")
  entries.find do |row|
    row[:host] == host &&
      (row[:rule].match?(path) || row[:rule].match?(URI::DEFAULT_PARSER.unescape(path)))
  end
end

valid = [
  %w[/two-factor-login-with-passkeys/ /nested/article_with-underscore/ /author-notes/ /2025/03-article/],
  %w[/dvoufaktorove-prihlasovani-s-passkey/ /ipv6-64/ /author-notes/ /123-clanek/]
]
rows.zip(valid).each do |row, paths|
  paths.each do |path|
    canonical = "https://#{row[:host]}#{path}"
    check.call(lookup.call(canonical, rows) == row, "Canonical host/category missing: #{canonical}")
    imported = normalize.call(canonical)
    check.call(lookup.call(imported, rows) == row, "Normalized host/category missing: #{imported}")
  end
end

reserved = %w[feed search author authors category categories tag tags archive archives page posts assets images pagefind admin login logout robots sitemap]
months = Dir.children(File.expand_path("../content/posts", __dir__)).filter_map do |name|
  name[/\A[0-9]{4}-[0-9]{2}(?=-)/]&.tr("-", "/")
end.uniq
check.call(months.include?("2025/03"), "Expected the actual pilot month archive")
rows.each_with_index do |row, index|
  excluded = reserved + (index.zero? ? %w[cs en] + months : %w[0 123 wp-123 wp-article])
  paths = ["/", "/nested//article", "/article?query=1", "/article/?query=1"]
  excluded.each { |root| paths.concat(["/#{root}", "/#{root}/", "/#{root}/article"]) }
  paths.each do |path|
    url = "https://#{row[:host]}#{path}"
    check.call(lookup.call(url, rows).nil?, "Excluded path selected a host: #{url}")
    check.call(lookup.call(normalize.call(url), rows).nil?, "Normalized excluded path selected a host: #{url}")
  end
end

pilot = guide.lines.filter_map do |line|
  match = line.match(/\A\s*(blog\.vpsfree\.(?:org|cz)):\s*(\\A\S+)\s*\z/)
  { host: match[1], rule: Regexp.new(match[2]), category: 10 } if match
end
check.call(pilot.map { |row| row[:host] } == hosts, "Expected both documented pilot rules")
pilot.each_with_index do |row, index|
  canonical = "https://#{row[:host]}#{valid[index].first}"
  check.call(lookup.call(canonical, pilot) == row, "Canonical pilot host/category missing")
  check.call(lookup.call(normalize.call(canonical), pilot) == row, "Normalized pilot host/category missing")
  check.call(lookup.call("https://#{row[:host]}/another-article/", pilot).nil?, "Pilot rule widened")
end

puts "PASS: documented discussion paths (#{checks} assertions; normalize then native Ruby host matching)"
