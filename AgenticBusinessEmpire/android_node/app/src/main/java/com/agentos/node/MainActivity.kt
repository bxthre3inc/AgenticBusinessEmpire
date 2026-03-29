package com.agentos.node

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.agentos.node.ui.theme.AgentOSTheme
import com.agentos.node.viewmodel.NodeViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Start the background mesh service
        MeshService.start(this)
        setContent {
            AgentOSTheme {
                AgentOSDashboard()
            }
        }
    }
}

@Composable
fun AgentOSDashboard(vm: NodeViewModel = viewModel()) {
    val state by vm.nodeState.collectAsState()

    val bgGradient = Brush.verticalGradient(
        colors = listOf(Color(0xFF090E1A), Color(0xFF0D1B2A), Color(0xFF112240))
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(bgGradient)
            .padding(20.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ── Header ──────────────────────────────────────────
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "🌌 AgentOS Node",
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF64FFDA)
                )
                Spacer(Modifier.weight(1f))
                StatusPill(state.status)
            }

            // ── Pressure Card ────────────────────────────────────
            GlassCard {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    MetricRow("CPU", "${state.cpuPercent}%", Color(0xFF64FFDA))
                    MetricRow("RAM Free", "${state.ramFreeMb}MB", Color(0xFF82AAFF))
                    MetricRow("Battery", "${state.batteryPercent}% ${if (state.isCharging) "⚡" else ""}", Color(0xFFFFCB6B))
                    MetricRow("Pressure Score", "${state.pressureScore}/100", pressureColor(state.pressureScore))
                    MetricRow("Mesh Role", state.role, Color(0xFFC3E88D))
                }
            }

            // ── Mesh Peers ───────────────────────────────────────
            GlassCard {
                Column {
                    Text("Mesh Peers", color = Color(0xFF8892B0), fontSize = 12.sp)
                    Spacer(Modifier.height(6.dp))
                    if (state.peers.isEmpty()) {
                        Text("Scanning for peers…", color = Color(0xFF495670), fontSize = 13.sp)
                    } else {
                        state.peers.forEach { peer ->
                            Text("● $peer", color = Color(0xFF64FFDA), fontSize = 13.sp)
                        }
                    }
                }
            }

            // ── Voice Controls ───────────────────────────────────
            GlassCard {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Button(
                        onClick = { vm.startListening() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B3A5C)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("🎙 Speak", color = Color.White)
                    }
                    Text(
                        state.lastCommand.ifEmpty { "Say a command..." },
                        color = Color(0xFF8892B0),
                        fontSize = 13.sp,
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            // ── Last Agent Response ──────────────────────────────
            if (state.lastResponse.isNotEmpty()) {
                GlassCard {
                    Column {
                        Text("Agent Response", color = Color(0xFF8892B0), fontSize = 12.sp)
                        Spacer(Modifier.height(4.dp))
                        Text(state.lastResponse, color = Color(0xFFCCD6F6), fontSize = 14.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun GlassCard(content: @Composable ColumnScope.() -> Unit) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = Color(0x1AFFFFFF),
        tonalElevation = 2.dp,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp), content = content)
    }
}

@Composable
fun MetricRow(label: String, value: String, valueColor: Color) {
    Row(modifier = Modifier.fillMaxWidth()) {
        Text(label, color = Color(0xFF8892B0), fontSize = 13.sp)
        Spacer(Modifier.weight(1f))
        Text(value, color = valueColor, fontSize = 13.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun StatusPill(status: String) {
    val (bg, label) = when (status) {
        "active" -> Color(0xFF1B4332) to "● Active"
        "idle"   -> Color(0xFF1A2540) to "○ Idle"
        else     -> Color(0xFF3D0000) to "✕ Offline"
    }
    Surface(shape = RoundedCornerShape(20.dp), color = bg) {
        Text(label, color = Color(0xFF64FFDA), fontSize = 11.sp, modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp))
    }
}

fun pressureColor(score: Int): Color = when {
    score < 40  -> Color(0xFF64FFDA)
    score < 70  -> Color(0xFFFFCB6B)
    else        -> Color(0xFFFF5370)
}
