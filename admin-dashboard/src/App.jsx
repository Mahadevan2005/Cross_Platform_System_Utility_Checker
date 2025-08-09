import React, { useState, useEffect } from "react";
import {
  Box,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Container,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TablePagination,
  Chip,
  CircularProgress,
} from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import SettingsIcon from "@mui/icons-material/Settings";

const drawerWidth = 240;
const API_URL = "http://localhost:8000/api/machines";
const API_KEY = "secret_key";

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) return -1;
  if (b[orderBy] > a[orderBy]) return 1;
  return 0;
}

function getComparator(order, orderBy) {
  return order === "desc"
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

function stableSort(array, comparator) {
  const stabilized = array.map((el, index) => [el, index]);
  stabilized.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilized.map((el) => el[0]);
}

function statusChip(label, color) {
  return <Chip label={label} color={color} size="small" />;
}

function hasIssues(machine) {
  return (
    !machine.disk_encryption ||
    !machine.os_is_up_to_date ||
    !machine.antivirus_present ||
    machine.inactivity_sleep_minutes > 10
  );
}

function formatTimestamp(ts) {
  if (!ts) return "-";
  const d = new Date(ts);
  return d.toLocaleString();
}

export default function Dashboard() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [order, setOrder] = useState("asc");
  const [orderBy, setOrderBy] = useState("machine_id");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const toggleDrawer = () => {
    setMobileOpen(!mobileOpen);
  };

  async function fetchMachines() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(API_URL, {
        headers: {
          "x-api-key": API_KEY,
        },
      });
      if (!res.ok) throw new Error(`Error ${res.status}`);

      const data = await res.json();
      setMachines(data.machines || []);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchMachines();
  }, []);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Solsphere Admin
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <ListItem button selected>
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button disabled>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: "primary.dark",
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2, display: { sm: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Solsphere System Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="sidebar navigation"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={toggleDrawer}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: "block", sm: "none" },
            "& .MuiDrawer-paper": { width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", sm: "block" },
            "& .MuiDrawer-paper": { width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        <Container maxWidth="lg">
          {/* Summary Cards */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Total Machines
                </Typography>
                <Typography variant="h4">{machines.length}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Machines with Issues
                </Typography>
                <Typography variant="h4">
                  {machines.filter((m) => hasIssues(m)).length}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Clean Machines
                </Typography>
                <Typography variant="h4">
                  {machines.filter((m) => !hasIssues(m)).length}
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Data Table */}
          <Paper elevation={3}>
            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                <CircularProgress />
              </Box>
            ) : error ? (
              <Typography color="error" sx={{ p: 2 }}>
                {error}
              </Typography>
            ) : (
              <>
                <TableContainer>
                  <Table aria-label="machines table" size="small">
                    <TableHead>
                      <TableRow>
                        {[
                          { id: "machine_id", label: "Machine ID" },
                          { id: "os_type", label: "OS Type" },
                          { id: "disk_encryption", label: "Disk Encryption" },
                          { id: "os_is_up_to_date", label: "OS Update Status" },
                          { id: "antivirus_present", label: "Antivirus" },
                          { id: "inactivity_sleep_minutes", label: "Inactivity Sleep (min)" },
                          { id: "last_check_in", label: "Last Check-in" },
                          { id: "issues", label: "Issues" },
                        ].map((headCell) => (
                          <TableCell
                            key={headCell.id}
                            sortDirection={orderBy === headCell.id ? order : false}
                          >
                            <TableSortLabel
                              active={orderBy === headCell.id}
                              direction={orderBy === headCell.id ? order : "asc"}
                              onClick={() => handleRequestSort(null, headCell.id)}
                            >
                              {headCell.label}
                            </TableSortLabel>
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {stableSort(machines, getComparator(order, orderBy))
                        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                        .map((m) => {
                          const issue = hasIssues(m);
                          return (
                            <TableRow
                              key={m.machine_id}
                              sx={{ bgcolor: issue ? "error.light" : "inherit" }}
                            >
                              <TableCell>{m.machine_id}</TableCell>
                              <TableCell>{m.os_type}</TableCell>
                              <TableCell>
                                {m.disk_encryption
                                  ? statusChip("Encrypted", "success")
                                  : statusChip("Not Encrypted", "error")}
                              </TableCell>
                              <TableCell>
                                {m.os_is_up_to_date
                                  ? statusChip("Up-to-date", "success")
                                  : statusChip("Outdated", "error")}
                              </TableCell>
                              <TableCell>
                                {m.antivirus_present
                                  ? statusChip("Present", "success")
                                  : statusChip("Not Present", "error")}
                              </TableCell>
                              <TableCell>{m.inactivity_sleep_minutes}</TableCell>
                              <TableCell>{formatTimestamp(m.last_check_in)}</TableCell>
                              <TableCell>
                                {issue ? statusChip("Issues", "error") : statusChip("Clean", "success")}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  component="div"
                  count={machines.length}
                  page={page}
                  onPageChange={handleChangePage}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  rowsPerPageOptions={[5, 10, 25]}
                />
              </>
            )}
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
