using Microsoft.AspNetCore.Identity.Data;
using Microsoft.AspNetCore.Mvc;
using Sentra.Application.Auth;

namespace Sentra.Api.Controllers;

[ApiController]
[Route("auth")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _auth;

    public AuthController(IAuthService auth) => _auth = auth;

    [HttpPost("token")]
    public async Task<IActionResult> Login([FromBody] LoginRequest req)
    {
        var result = await _auth.Login(req.Username, req.Password);
        return Ok(result);
    }

    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh([FromBody] RefreshRequest req)
    {
        var result = await _auth.Refresh(req.RefreshToken);
        return Ok(result);
    }
}
