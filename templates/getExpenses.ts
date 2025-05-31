import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";
/**
 * Get this month's expenses to-do list.
 */
export default (): string => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  const fmt = `YYYY-MM-DDTHHmmssZZ`;
  const now = tp.obsidian.moment();
  const monthYear = now.format("MMMM YYYY");
  return `\
### Enter ${monthYear} expenses 🆔 ${now.format(fmt)}

- [ ] [Enter ${monthYear} expenses](#Enter%20${encodeURIComponent(monthYear)}%20expenses%20🆔%20${now.format(fmt)}) 🆔 ${now.add(1, "seconds").format(fmt)}
    - [ ] Download transactions to [\`2025-04-01T15-54-31-transactions\`](file:///G:/My%20Drive/Blake/Other/Finance/Budget/2025-04-01T15-54-31-transactions) 🆔 ${now.add(1, "seconds").format(fmt)}
        - Download [Bank of America transactions](https://secure.bankofamerica.com/myaccounts/details/card)
        - Download [Capital One transactions](https://myaccounts.capitalone.com/accountSummary)
        - Download [Chase transactions](https://secure.chase.com/web/auth/dashboard#/dashboard/accountDetails/downloadAccountTransactions/index)
        - Download [Discover transactions](https://card.discover.com/cardmembersvcs/statements/app/activity#/recent)
    - [ ] Import transactions [\`2025-04-01T15-54-31-transactions.xlsx\`](file:///G:/My%20Drive/Blake/Other/Finance/Budget/2025-04-01T15-54-31-transactions.xlsx) 🆔 ${now.add(1, "seconds").format(fmt)}
    - [ ] Categorize transactions 🆔 ${now.add(1, "seconds").format(fmt)}
    - [ ] Add to [\`Budgeting 2025.xlsx\`](file:///G:/My%20Drive/Tiana/Budgeting%202025.xlsx) 🆔 ${now.add(1, "seconds").format(fmt)}
    - [ ] Determine amount of transfer needed
- [ ] Get transfer from Tiana`;
};
