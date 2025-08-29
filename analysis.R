 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/analysis.R
index 0000000000000000000000000000000000000000..bdf3a673e0265fd233f5a1c7daa52b7a0cd52dce 100644
--- a//dev/null
+++ b/analysis.R
@@ -0,0 +1,12 @@
+library(RSQLite)
+library(ggplot2)
+args <- commandArgs(trailingOnly=TRUE)
+db_path <- ifelse(length(args) >= 1, args[1], "simulation.db")
+conn <- dbConnect(SQLite(), db_path)
+bankroll <- dbReadTable(conn, "bankroll")
+ggplot(bankroll, aes(x=hand, y=bankroll, color=factor(trial))) + geom_line() + theme_minimal()
+ggsave("bankroll.png")
+dist <- dbReadTable(conn, "card_distribution")
+ggplot(dist, aes(x=card, y=count, fill=factor(trial))) + geom_bar(stat="identity", position="dodge") + theme_minimal()
+ggsave("distribution.png")
+dbDisconnect(conn)
 
EOF
)
