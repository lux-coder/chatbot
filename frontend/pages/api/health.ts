import type { NextApiRequest, NextApiResponse } from 'next'

interface HealthResponse {
  status: 'ok' | 'error'
  timestamp: string
  version?: string
  uptime: number
  checks: {
    [key: string]: 'ok' | 'error'
  }
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET'])
    res.status(405).json({
      status: 'error',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks: {
        method: 'error'
      }
    })
    return
  }

  try {
    // Basic health checks
    const checks: { [key: string]: 'ok' | 'error' } = {
      server: 'ok',
      memory: 'ok',
      environment: 'ok'
    }

    // Check memory usage (mark as error if over 90% of limit)
    const memUsage = process.memoryUsage()
    const memUsagePercent = (memUsage.heapUsed / memUsage.heapTotal) * 100
    if (memUsagePercent > 90) {
      checks['memory'] = 'error'
    }

    // Check environment variables
    const requiredEnvVars = [
      'NEXT_PUBLIC_API_URL',
      'NEXT_PUBLIC_KEYCLOAK_URL',
      'NEXT_PUBLIC_KEYCLOAK_REALM',
      'NEXT_PUBLIC_KEYCLOAK_CLIENT_ID'
    ]

    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar]) {
        checks['environment'] = 'error'
        break
      }
    }

    // Determine overall status
    const hasErrors = Object.values(checks).includes('error')
    const status = hasErrors ? 'error' : 'ok'

    const response: HealthResponse = {
      status,
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      uptime: process.uptime(),
      checks
    }

    // Set appropriate status code
    const statusCode = status === 'ok' ? 200 : 503
    
    res.status(statusCode).json(response)
    
  } catch (error) {
    console.error('Health check error:', error)
    
    res.status(503).json({
      status: 'error',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks: {
        server: 'error'
      }
    })
  }
} 