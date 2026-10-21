-- ArashiOS Neovim defaults. No external plugin manager required.
vim.g.mapleader = " "
vim.g.maplocalleader = " "

vim.opt.termguicolors = true
vim.opt.background = "dark"
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.expandtab = true
vim.opt.smartindent = true
vim.opt.wrap = false
vim.opt.cursorline = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 250
vim.opt.timeoutlen = 400
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.scrolloff = 8
vim.opt.sidescrolloff = 8
vim.opt.list = true
vim.opt.listchars = "tab:> ,trail:·,nbsp:·"
vim.opt.laststatus = 2
vim.opt.statusline = "%f %m %= %l:%c"

vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_browse_split = 4
vim.g.netrw_winsize = 25

vim.cmd("filetype plugin indent on")
vim.cmd("syntax enable")

local function hl(group, value)
  vim.api.nvim_set_hl(0, group, value)
end

hl("Normal", { fg = "#EDE8DE", bg = "#0A0A0C" })
hl("Comment", { fg = "#8B867D" })
hl("String", { fg = "#5FA88C" })
hl("Keyword", { fg = "#DD785B" })
hl("Function", { fg = "#D6B36A" })
hl("Type", { fg = "#E8917A" })
hl("Constant", { fg = "#D6B36A" })
hl("Identifier", { fg = "#EDE8DE" })
hl("Statement", { fg = "#DD785B" })
hl("PreProc", { fg = "#E8917A" })
hl("Special", { fg = "#5FA88C" })
hl("Visual", { bg = "#25252D" })
hl("LineNr", { fg = "#6B675F" })
hl("CursorLineNr", { fg = "#DD785B", bold = true })
hl("CursorLine", { bg = "#121216" })
hl("StatusLine", { fg = "#EDE8DE", bg = "#121216" })
hl("StatusLineNC", { fg = "#8B867D", bg = "#121216" })
hl("Pmenu", { fg = "#EDE8DE", bg = "#1B1B21" })
hl("PmenuSel", { fg = "#070709", bg = "#DD785B" })
hl("Search", { fg = "#070709", bg = "#D6B36A" })
hl("IncSearch", { fg = "#070709", bg = "#DD785B" })
hl("MatchParen", { fg = "#DD785B", bold = true })
hl("DiagnosticError", { fg = "#D05545" })
hl("DiagnosticWarn", { fg = "#D6B36A" })
hl("DiagnosticInfo", { fg = "#5FA88C" })
hl("DiagnosticHint", { fg = "#8B867D" })
hl("DiffAdd", { fg = "#5FA88C", bg = "#121216" })
hl("DiffChange", { fg = "#D6B36A", bg = "#121216" })
hl("DiffDelete", { fg = "#D05545", bg = "#121216" })

vim.keymap.set("n", "<leader>w", ":w<CR>", { desc = "Write file" })
vim.keymap.set("n", "<leader>q", ":q<CR>", { desc = "Quit" })
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlight" })
vim.keymap.set("n", "<leader>e", ":Ex<CR>", { desc = "File explorer" })
vim.keymap.set("n", "<C-h>", "<C-w>h", { desc = "Window left" })
vim.keymap.set("n", "<C-j>", "<C-w>j", { desc = "Window down" })
vim.keymap.set("n", "<C-k>", "<C-w>k", { desc = "Window up" })
vim.keymap.set("n", "<C-l>", "<C-w>l", { desc = "Window right" })

vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function()
    vim.highlight.on_yank({ higroup = "IncSearch", timeout = 150 })
  end,
})
