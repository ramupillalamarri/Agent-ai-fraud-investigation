import { investigationApi } from "./investigation";

export const dashboardApi = {
  /**
   * Aggregates live database statistics for the main analyst dashboard page
   */
  getSummary: async () => {
    const { investigations, total } = await investigationApi.list({ page_size: 100 });
    
    const highRiskCount = investigations.filter((i: any) => i.priority === "HIGH" || i.risk_score >= 80).length;
    
    const totalRiskScore = investigations.reduce((sum: number, i: any) => sum + (i.risk_score || 0), 0);
    const averageRiskScore = investigations.length > 0 ? Math.round(totalRiskScore / investigations.length) : 0;
    
    // Fraud classification rate (percentage of investigations flagged as high risk)
    const fraudCases = investigations.filter((i: any) => (i.risk_score || 0) >= 75).length;
    const fraudDetectionRate = investigations.length > 0 
      ? Math.round((fraudCases / investigations.length) * 100) 
      : 0;

    // Agent metrics
    let totalTime = 0;
    let successCount = 0;
    let totalCount = 0;
    
    investigations.forEach((inv: any) => {
      if (inv.agent_results) {
        inv.agent_results.forEach((ar: any) => {
          totalTime += ar.execution_time_ms || 0;
          if (ar.status === "SUCCESS") successCount++;
          totalCount++;
        });
      }
    });

    const avgExecutionTimeMs = totalCount > 0 ? Math.round(totalTime / totalCount) : 0;
    const agentSuccessRate = totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 100;

    return {
      totalInvestigations: total,
      highRiskInvestigations: highRiskCount,
      averageRiskScore,
      fraudDetectionRate,
      avgExecutionTimeMs,
      agentSuccessRate,
      recentInvestigations: investigations.slice(0, 5)
    };
  }
};
